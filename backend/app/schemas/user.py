from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    email: str
    name: str
    profile_picture: str | None = None


class UserCreate(UserBase):
    id: str


class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }