from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.services.ingestion import extract_text_from_pdf, save_chunks

router = APIRouter(prefix="/upload", tags=["Upload"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    contents = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"PDF files must be smaller than {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    stored_filename = f"{uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / stored_filename
    file_path.write_bytes(contents)

    document = Document(
        title=Path(filename.replace("\\", "/")).stem,
        filename=Path(filename.replace("\\", "/")).name,
        file_url=str(file_path),
        summary="",
        status="Processing",
        owner_id=user.id
    )

    try:
        db.add(document)
        db.flush()
        pages = extract_text_from_pdf(str(file_path))
        if not any(text.strip() for _, text in pages):
            raise HTTPException(
                status_code=422,
                detail="No selectable text was found in this PDF.",
            )
        chunk_count = save_chunks(db=db, document_id=document.id, pages=pages)
        if not chunk_count:
            raise HTTPException(
                status_code=422,
                detail="No text could be split into searchable chunks.",
            )
        document.status = "Completed"
        db.commit()
    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise

    return {
        "message": "PDF uploaded successfully.",
        "document_id": document.id,
        "title": document.title,
        "filename": document.filename,
        "chunk_count": chunk_count,
    }