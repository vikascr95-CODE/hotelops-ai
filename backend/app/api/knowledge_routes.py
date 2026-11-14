
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetail
from app.services.document_service import create_document

router = APIRouter(
    prefix="/knowledge",
    tags=["AI Knowledge Base"],
)


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await create_document(db, file)


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)

    if not document:
        from fastapi import HTTPException
        raise HTTPException(404, "Document not found")

    return {
        "id": document.id,
        "filename": document.filename,
        "original_filename": document.original_filename,
        "content_type": document.content_type,
        "file_size": document.file_size,
        "created_at": document.created_at,
        "extracted_text": document.extracted_text,
        "chunks": [chunk.content for chunk in document.chunks],
    }
