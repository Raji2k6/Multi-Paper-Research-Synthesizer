from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    filename: str
    file_url: str
    summary: str | None
    status: str
    uploaded_at: datetime
    owner_id: str

    model_config = {
        "from_attributes": True
    }