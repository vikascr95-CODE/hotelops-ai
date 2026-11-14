
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session
from pypdf.errors import PdfReadError

from app.ai.chunking import chunk_text
from app.models.document import Document, DocumentChunk

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024


def extract_text(file_path: Path, extension: str) -> str:
    if extension == ".txt":
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise HTTPException(422, "Text files must be UTF-8 encoded.")

    try:
        reader = PdfReader(str(file_path))
    except PdfReadError:
        raise HTTPException(422, "This PDF could not be read. It may be corrupted.")

    if reader.is_encrypted:
        raise HTTPException(422, "Password-protected PDFs are not supported.")

    return "\n".join(page.extract_text() or "" for page in reader.pages)


async def create_document(db: Session, file: UploadFile):
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if extension not in {".pdf", ".txt"}:
        raise HTTPException(400, "Only PDF and TXT files are supported.")

    content = await file.read()

    if not content:
        raise HTTPException(400, "The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "Maximum file size is 10 MB.")

    safe_filename = f"{uuid4().hex}{extension}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / safe_filename

    try:
        file_path.write_bytes(content)
        text = extract_text(file_path, extension)

        if not text.strip():
            raise HTTPException(
                422,
                "No readable text found. Scanned PDFs need OCR.",
            )

        chunks = chunk_text(text)

        document = Document(
            filename=safe_filename,
            original_filename=original_name,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            extracted_text=text,
        )

        document.chunks = [
            DocumentChunk(chunk_index=index, content=chunk)
            for index, chunk in enumerate(chunks)
        ]

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise
