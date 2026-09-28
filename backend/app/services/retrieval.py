from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.chunk import Chunk
from app.services.embeddings import generate_embedding


def retrieve_relevant_chunks(
    db: Session,
    question: str,
    top_k: int = 5
):
    """
    Retrieve the top-k most similar chunks using pgvector.
    """

    embedding = generate_embedding(question)

    sql = text("""
    SELECT
        chunks.id,
        chunks.content,
        chunks.page_number,
        chunks.document_id,
        documents.title AS document_title,
        documents.filename AS document_filename,
        chunks.embedding <=> CAST(:embedding AS vector) AS distance
    FROM chunks
    JOIN documents
        ON chunks.document_id = documents.id
    ORDER BY chunks.embedding <=> CAST(:embedding AS vector)
    LIMIT :top_k
    """)

    result = db.execute(
        sql,
        {
            "embedding": str(embedding),
            "top_k": top_k
        }
    )

    return result.fetchall()


def build_context(chunks):
    """
    Convert retrieved chunks into a paper-aware context string.
    """

    context = ""

    for chunk in chunks:
        context += (
            f"[Paper: {chunk.document_title}]\n"
            f"[Page: {chunk.page_number}]\n"
            f"{chunk.content}\n\n"
        )

    return context.strip()

def extract_sources(chunks):
    """
    Extract paper and page information from retrieved chunks.
    """

    sources = []

    for chunk in chunks:
        source = {
            "document_id": chunk.document_id,
            "document_title": chunk.document_title,
            "page": chunk.page_number
        }

        if source not in sources:
            sources.append(source)

    return sources

def group_chunks_by_document(chunks):
    """
    Group retrieved chunks by document.
    """

    grouped = {}

    for chunk in chunks:
        document_id = chunk.document_id

        if document_id not in grouped:
            grouped[document_id] = {
                "document_id": document_id,
                "document_title": chunk.document_title,
                "filename": chunk.document_filename,
                "chunks": []
            }

        grouped[document_id]["chunks"].append({
            "page": chunk.page_number,
            "content": chunk.content,
            "distance": chunk.distance
        })

    return list(grouped.values())

def build_paper_context(grouped_documents):
    """
    Build a structured context organized by paper.
    """

    context = ""

    for document in grouped_documents:

        context += (
            f"===== PAPER =====\n"
            f"Document ID: {document['document_id']}\n"
            f"Title: {document['document_title']}\n"
            f"Filename: {document['filename']}\n"
            f"=================\n\n"
        )

        for chunk in document["chunks"]:
            context += (
                f"[Page {chunk['page']}]\n"
                f"{chunk['content']}\n\n"
            )

    return context.strip()

def retrieve_chunks_per_document(
    db: Session,
    question: str,
    chunks_per_document: int = 3
):
    """
    Retrieve relevant chunks separately for each document.

    This is used for multi-paper analysis so that one document
    does not dominate the retrieved evidence.
    """

    # Generate embedding for the user's question
    embedding = generate_embedding(question)

    # First find which documents have relevant chunks
    document_sql = text("""
        SELECT DISTINCT document_id
        FROM chunks
        WHERE embedding IS NOT NULL
    """)

    document_result = db.execute(document_sql)

    document_ids = [
        row.document_id
        for row in document_result
    ]

    all_chunks = []

    # Retrieve top chunks separately for every document
    for document_id in document_ids:

        sql = text("""
            SELECT
                chunks.id,
                chunks.content,
                chunks.page_number,
                chunks.document_id,
                documents.title AS document_title,
                documents.filename AS document_filename,
                chunks.embedding <=> CAST(:embedding AS vector) AS distance
            FROM chunks
            JOIN documents
                ON chunks.document_id = documents.id
            WHERE chunks.document_id = :document_id
            ORDER BY chunks.embedding <=> CAST(:embedding AS vector)
            LIMIT :chunks_per_document
        """)

        result = db.execute(
            sql,
            {
                "embedding": str(embedding),
                "document_id": document_id,
                "chunks_per_document": chunks_per_document
            }
        )

        all_chunks.extend(result.fetchall())

    # Sort all retrieved chunks by similarity
    all_chunks.sort(key=lambda chunk: chunk.distance)

    return all_chunks


def retrieve_relevant_chunks_per_document(
    db: Session,
    question: str,
    chunks_per_document: int = 3,
    candidate_k: int = 10,
    max_distance: float = 0.75
):
    """
    Retrieve relevant chunks from each relevant document.

    Process:
    1. Perform a global semantic search.
    2. Identify documents that have sufficiently relevant chunks.
    3. Retrieve a balanced number of chunks from each relevant document.
    4. Ignore documents that are not relevant to the question.
    """

    embedding = generate_embedding(question)

    # ---------------------------------------------------------
    # Step 1: Find globally relevant chunks
    # ---------------------------------------------------------

    candidate_sql = text("""
        SELECT
            chunks.id,
            chunks.content,
            chunks.page_number,
            chunks.document_id,
            documents.title AS document_title,
            documents.filename AS document_filename,
            chunks.embedding <=> CAST(:embedding AS vector) AS distance
        FROM chunks
        JOIN documents
            ON chunks.document_id = documents.id
        WHERE chunks.embedding IS NOT NULL
        ORDER BY chunks.embedding <=> CAST(:embedding AS vector)
        LIMIT :candidate_k
    """)

    candidate_result = db.execute(
        candidate_sql,
        {
            "embedding": str(embedding),
            "candidate_k": candidate_k
        }
    )

    candidates = candidate_result.fetchall()

    # ---------------------------------------------------------
    # Step 2: Identify relevant documents
    # ---------------------------------------------------------

    relevant_document_ids = []

    for chunk in candidates:

        if chunk.distance <= max_distance:

            if chunk.document_id not in relevant_document_ids:
                relevant_document_ids.append(
                    chunk.document_id
                )

    # ---------------------------------------------------------
    # Step 3: Retrieve balanced chunks from each
    # relevant document
    # ---------------------------------------------------------

    all_chunks = []

    for document_id in relevant_document_ids:

        sql = text("""
            SELECT
                chunks.id,
                chunks.content,
                chunks.page_number,
                chunks.document_id,
                documents.title AS document_title,
                documents.filename AS document_filename,
                chunks.embedding <=> CAST(:embedding AS vector) AS distance
            FROM chunks
            JOIN documents
                ON chunks.document_id = documents.id
            WHERE
                chunks.document_id = :document_id
                AND chunks.embedding IS NOT NULL
            ORDER BY chunks.embedding <=> CAST(:embedding AS vector)
            LIMIT :chunks_per_document
        """)

        result = db.execute(
            sql,
            {
                "embedding": str(embedding),
                "document_id": document_id,
                "chunks_per_document": chunks_per_document
            }
        )

        all_chunks.extend(
            result.fetchall()
        )

    # ---------------------------------------------------------
    # Step 4: Sort all selected chunks by relevance
    # ---------------------------------------------------------

    all_chunks.sort(
        key=lambda chunk: chunk.distance
    )

    return all_chunks