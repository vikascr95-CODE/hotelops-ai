from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.rag_engine import best_sentences, rank_chunks
from app.database.connection import get_db
from app.models.document import Document, DocumentChunk
from app.schemas.knowledge import AskRequest, AskResponse, Source

router = APIRouter(prefix="/knowledge", tags=["AI Knowledge Base"])

NOT_FOUND_ANSWER = "I could not find this in the uploaded documents."


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)):
    rows = db.execute(
        select(DocumentChunk, Document.original_filename).join(
            Document, Document.id == DocumentChunk.document_id
        )
    ).all()

    chunks = [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "document": filename,
            "chunk_index": chunk.chunk_index,
            "text": chunk.content,
        }
        for chunk, filename in rows
    ]

    matches = rank_chunks(payload.question, chunks, top_k=payload.top_k)

    if not matches:
        return AskResponse(
            question=payload.question,
            answer=NOT_FOUND_ANSWER,
            grounded=False,
            sources=[],
        )

    answer = best_sentences(payload.question, matches[0]["text"])
    sources = [
        Source(
            document_id=m["document_id"],
            document=m["document"],
            chunk_index=m["chunk_index"],
            score=m["score"],
            excerpt=m["text"][:200],
        )
        for m in matches
    ]
    return AskResponse(
        question=payload.question, answer=answer, grounded=True, sources=sources
    )