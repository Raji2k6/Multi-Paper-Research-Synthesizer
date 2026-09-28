import os
import shutil

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.document import Document
from app.services.ingestion import extract_text_from_pdf, save_chunks

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create document record
    document = Document(
        title=file.filename.replace(".pdf", ""),
        filename=file.filename,
        file_url=file_path,
        summary="",
        status="Processing",
        owner_id="demo_user"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Extract text
    pages = extract_text_from_pdf(file_path)

    # Save chunks
    save_chunks(
        db=db,
        document_id=document.id,
        pages=pages
    )

    # Update status
    document.status = "Completed"
    db.commit()

    return {
        "message": "PDF uploaded successfully.",
        "document_id": document.id
    }