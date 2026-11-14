
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetail(DocumentResponse):
    extracted_text: str
    chunks: list[str]
