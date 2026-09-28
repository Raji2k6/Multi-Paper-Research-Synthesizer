from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.query import QueryCreate

from app.services.retrieval import (
    retrieve_relevant_chunks_per_document,
    group_chunks_by_document,
    build_paper_context,
    extract_sources,
)

from app.services.comparison import compare_papers


router = APIRouter(
    prefix="/synthesis",
    tags=["Multi-Paper Synthesis"]
)


@router.post("/")
def synthesis(
    request: QueryCreate,
    db: Session = Depends(get_db)
):
    # Retrieve relevant evidence from multiple documents
    chunks = retrieve_relevant_chunks_per_document(
        db=db,
        question=request.question,
        chunks_per_document=3,
        candidate_k=10,
        max_distance=0.75
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found."
        )

    # Group retrieved chunks by document
    grouped_documents = group_chunks_by_document(chunks)

    # Multi-paper comparison requires at least two documents
    if len(grouped_documents) < 2:
        raise HTTPException(
            status_code=400,
            detail=(
                "At least two relevant documents are required "
                "for multi-paper synthesis."
            )
        )

    # Build structured paper context
    paper_context = build_paper_context(grouped_documents)

    # Generate evidence-grounded comparison
    answer = compare_papers(
        question=request.question,
        paper_context=paper_context
    )

    # Extract source information
    sources = extract_sources(chunks)

    return {
        "question": request.question,
        "answer": answer,
        "documents_analyzed": len(grouped_documents),
        "sources": sources
    }