from pydantic import BaseModel
from datetime import datetime


class QueryCreate(BaseModel):
    question: str


class QueryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    user_id: str

    model_config = {
        "from_attributes": True
    }