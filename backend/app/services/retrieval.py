from types import SimpleNamespace

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embeddings import generate_embedding


def _search_chunks(
    db: Session,
    user_id: str,
    embedding: list[float],
    limit: int,
    document_id: int | None = None,
):
    if db.get_bind().dialect.name == "sqlite":
        query = (
            db.query(Chunk, Document)
            .join(Document)
            .filter(Document.owner_id == user_id)
        )
        if document_id is not None:
            query = query.filter(Chunk.document_id == document_id)

        query_vector = np.asarray(embedding, dtype=np.float32)
        results = []
        for chunk, document in query.all():
            stored_vector = np.asarray(chunk.embedding, dtype=np.float32)
            denominator = np.linalg.norm(query_vector) * np.linalg.norm(stored_vector)
            similarity = float(np.dot(query_vector, stored_vector) / denominator) if denominator else 0.0
            results.append(
                SimpleNamespace(
                    id=chunk.id,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    document_id=chunk.document_id,
                    document_title=document.title,
                    document_filename=document.filename,
                    distance=1.0 - similarity,
                )
            )

        return sorted(results, key=lambda chunk: chunk.distance)[:limit]

    sql = """
        SELECT
            chunks.id,
            chunks.content,
            chunks.page_number,
            chunks.document_id,
            documents.title AS document_title,
            documents.filename AS document_filename,
            chunks.embedding <=> CAST(:embedding AS vector) AS distance
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
        WHERE documents.owner_id = :user_id
    """
    parameters = {"embedding": str(embedding), "limit": limit, "user_id": user_id}
    if document_id is not None:
        sql += " AND chunks.document_id = :document_id"
        parameters["document_id"] = document_id
    sql += """
        ORDER BY chunks.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """
    return db.execute(text(sql), parameters).fetchall()


def retrieve_relevant_chunks(
    db: Session,
    user_id: str,
    question: str,
    top_k: int = 5,
):
    return _search_chunks(db, user_id, generate_embedding(question), top_k)


def build_context(chunks):
    return "\n\n".join(
        f"[Paper: {chunk.document_title}]\n"
        f"[Page: {chunk.page_number}]\n"
        f"{chunk.content}"
        for chunk in chunks
    )


def extract_sources(chunks):
    sources = []
    seen = set()
    for chunk in chunks:
        key = (chunk.document_id, chunk.page_number)
        if key not in seen:
            seen.add(key)
            sources.append(
                {
                    "document_id": chunk.document_id,
                    "document_title": chunk.document_title,
                    "page": chunk.page_number,
                }
            )
    return sources


def group_chunks_by_document(chunks):
    grouped = {}
    for chunk in chunks:
        if chunk.document_id not in grouped:
            grouped[chunk.document_id] = {
                "document_id": chunk.document_id,
                "document_title": chunk.document_title,
                "filename": chunk.document_filename,
                "chunks": [],
            }
        grouped[chunk.document_id]["chunks"].append(
            {
                "page": chunk.page_number,
                "content": chunk.content,
                "distance": chunk.distance,
            }
        )
    return list(grouped.values())


def build_paper_context(grouped_documents):
    sections = []
    for document in grouped_documents:
        chunks = "\n\n".join(
            f"[Page {chunk['page']}]\n{chunk['content']}"
            for chunk in document["chunks"]
        )
        sections.append(
            f"===== PAPER =====\n"
            f"Title: {document['document_title']}\n"
            f"Filename: {document['filename']}\n"
            f"=================\n\n{chunks}"
        )
    return "\n\n".join(sections)


def retrieve_chunks_per_document(
    db: Session,
    user_id: str,
    question: str,
    chunks_per_document: int = 3,
):
    embedding = generate_embedding(question)
    document_ids = (
        db.query(Chunk.document_id)
        .join(Document)
        .filter(Chunk.embedding.is_not(None), Document.owner_id == user_id)
        .distinct()
        .all()
    )
    chunks = []
    for (document_id,) in document_ids:
        chunks.extend(
            _search_chunks(db, user_id, embedding, chunks_per_document, document_id)
        )
    return sorted(chunks, key=lambda chunk: chunk.distance)


def retrieve_relevant_chunks_per_document(
    db: Session,
    user_id: str,
    question: str,
    chunks_per_document: int = 3,
    candidate_k: int = 10,
    max_distance: float = 0.75,
):
    embedding = generate_embedding(question)
    candidates = _search_chunks(db, user_id, embedding, candidate_k)
    relevant_document_ids = list(
        dict.fromkeys(
            chunk.document_id
            for chunk in candidates
            if chunk.distance <= max_distance
        )
    )

    chunks = []
    for document_id in relevant_document_ids:
        chunks.extend(
            _search_chunks(db, user_id, embedding, chunks_per_document, document_id)
        )
    return sorted(chunks, key=lambda chunk: chunk.distance)
