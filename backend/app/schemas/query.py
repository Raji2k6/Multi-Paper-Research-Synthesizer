from pydantic import BaseModel, Field
from datetime import datetime


class QueryCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    user_id: str

    model_config = {
        "from_attributes": True
    }