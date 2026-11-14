from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    document_id: int
    document: str
    chunk_index: int
    score: float
    excerpt: str


class AskResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    sources: list[Source]