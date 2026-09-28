from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.query import QueryCreate
from app.models.query import Query

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
    db: Session = Depends(get_db)
):
    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(
        db,
        request.question
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
        user_id="demo_user"
    )

    db.add(query)
    db.commit()

    return {
    "question": request.question,
    "answer": answer,
    "sources": sources
}