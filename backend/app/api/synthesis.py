from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.query import Query
from app.models.user import User
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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Retrieve relevant evidence from multiple documents
    chunks = retrieve_relevant_chunks_per_document(
        db=db,
        user_id=user.id,
        question=request.question,
        chunks_per_document=settings.SYNTHESIS_CHUNKS_PER_DOCUMENT,
        candidate_k=settings.SYNTHESIS_CANDIDATE_K,
        max_distance=settings.SYNTHESIS_MAX_DISTANCE,
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
    db.add(
        Query(
            question=request.question,
            answer=answer,
            user_id=user.id,
            query_type="synthesis",
            sources=sources,
            documents_analyzed=len(grouped_documents),
        )
    )
    db.commit()

    return {
        "question": request.question,
        "answer": answer,
        "documents_analyzed": len(grouped_documents),
        "sources": sources
    }


@router.get("/history")
def synthesis_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    history = (
        db.query(Query)
        .filter(Query.user_id == user.id, Query.query_type == "synthesis")
        .order_by(Query.created_at.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "sources": item.sources or [],
            "documents_analyzed": item.documents_analyzed or 0,
            "created_at": item.created_at,
        }
        for item in history
    ]