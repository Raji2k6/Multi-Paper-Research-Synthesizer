from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)
    query_type = Column(String(20), nullable=False, default="chat", server_default="chat")
    sources = Column(JSON, nullable=True)
    documents_analyzed = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="queries"
    )