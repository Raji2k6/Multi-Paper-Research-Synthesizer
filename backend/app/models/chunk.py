from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)

    page_number = Column(Integer, nullable=False)

    embedding = Column(Vector(384).with_variant(JSON(), "sqlite"), nullable=False)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )