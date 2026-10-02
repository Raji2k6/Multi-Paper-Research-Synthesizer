from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    documents = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    queries = relationship(
        "Query",
        back_populates="user",
        cascade="all, delete-orphan"
    )