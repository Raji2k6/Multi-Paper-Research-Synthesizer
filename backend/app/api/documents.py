import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.document import Document
from app.models.user import User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return [
        {
            "document_id": document.id,
            "title": document.title,
            "filename": document.filename,
            "status": document.status,
            "uploaded_at": document.uploaded_at,
            "chunk_count": len(document.chunks),
        }
        for document in documents
    ]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == user.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    stored_path = Path(document.file_url).resolve()
    upload_root = UPLOAD_DIR.resolve()
    db.delete(document)
    db.commit()

    if stored_path.is_relative_to(upload_root):
        try:
            stored_path.unlink(missing_ok=True)
        except OSError as error:
            logger.exception("Document record was deleted but its PDF could not be removed.")
            raise HTTPException(
                status_code=500,
                detail="The document was removed from the library, but its PDF file could not be removed.",
            ) from error
    else:
        logger.error("Skipped cleanup of document file outside the upload directory.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
