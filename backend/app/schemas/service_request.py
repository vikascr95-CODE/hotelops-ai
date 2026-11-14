
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ServiceRequestCreate(BaseModel):
    guest_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    reservation_id: Optional[int] = Field(None, gt=0)

    request_type: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=3)

    priority: Literal["low", "normal", "high", "urgent"] = "normal"


class ServiceRequestUpdate(BaseModel):
    request_type: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=3)
    priority: Optional[Literal["low", "normal", "high", "urgent"]] = None


class ServiceRequestStatusUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed", "cancelled"]


class ServiceRequestResponse(BaseModel):
    id: int
    guest_id: int
    room_id: int
    reservation_id: Optional[int]

    request_type: str
    description: str
    status: str
    priority: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
