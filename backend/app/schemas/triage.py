from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.service_request import ServiceRequestResponse


class TriageRequest(BaseModel):
    description: str = Field(min_length=3, max_length=1000)


class TriageResult(BaseModel):
    category: str
    priority: Literal["low", "normal", "high", "urgent"]
    team: str
    confidence: float
    needs_review: bool
    reasons: list[str]


class ApplyResponse(BaseModel):
    applied: bool
    message: str
    changes: list[str]
    triage: TriageResult
    service_request: ServiceRequestResponse