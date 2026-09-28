from pydantic import BaseModel


class ChunkResponse(BaseModel):
    id: int
    content: str
    page_number: int
    document_id: int

    model_config = {
        "from_attributes": True
    }