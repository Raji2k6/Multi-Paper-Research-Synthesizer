import pdfplumber
import re

from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embeddings import generate_embeddings


CHUNK_SIZE = 500

def extract_text_from_pdf(pdf_path: str) -> list[tuple[int, str]]:
    """
    Extract text from each page of the PDF.
    Returns: [(page_number, text)]
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, text))

    return pages


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE):
    """
    Split text into approximately chunk_size characters.
    """
    chunks = []
    current = ""

    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        if not sentence:
            continue
        if len(current) + len(sentence) < chunk_size:
            current += " " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


def save_chunks(
    db: Session,
    document_id: int,
    pages: list[tuple[int, str]]
):
    """
    Create embeddings and save chunks.
    """
    pending_chunks = []
    for page_number, text in pages:
        chunks = split_into_chunks(text)
        for chunk in chunks:
            pending_chunks.append((page_number, chunk))

    if not pending_chunks:
        return 0

    embeddings = generate_embeddings([chunk for _, chunk in pending_chunks])
    for (page_number, content), embedding in zip(pending_chunks, embeddings):
        db.add(
            Chunk(
                content=content,
                page_number=page_number,
                embedding=embedding,
                document_id=document_id,
            )
        )

    return len(pending_chunks)