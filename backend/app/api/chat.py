from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.query import Query
from app.models.user import User
from app.schemas.query import QueryCreate

from app.services.retrieval import (
    retrieve_relevant_chunks,
    build_context,
    extract_sources,
)
from app.services.llm import generate_answer

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(
    request: QueryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(
        db,
        user.id,
        request.question,
        top_k=settings.RETRIEVAL_TOP_K,
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found."
        )

    # Build context
    context = build_context(chunks)

    # Extract sources
    sources = extract_sources(chunks)

    # Generate answer
    answer = generate_answer(
        request.question,
        context
    )

    # Save query history
    query = Query(
        question=request.question,
        answer=answer,
        user_id=user.id,
        query_type="chat",
        sources=sources,
    )

    db.add(query)
    db.commit()

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }


@router.get("/history")
def chat_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    history = (
        db.query(Query)
        .filter(Query.user_id == user.id, Query.query_type == "chat")
        .order_by(Query.created_at.asc())
        .all()
    )
    return [
        {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "sources": item.sources or [],
            "created_at": item.created_at,
        }
        for item in history
    ]