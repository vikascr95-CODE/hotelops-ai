
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20)
    room_type: str = Field(..., min_length=1, max_length=50)
    floor: int = Field(..., ge=0)
    capacity: int = Field(..., gt=0)
    price_per_night: Decimal = Field(..., gt=0)
    status: str = "available"
    is_active: bool = True


class RoomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, min_length=1, max_length=20)
    room_type: Optional[str] = Field(None, min_length=1, max_length=50)
    floor: Optional[int] = Field(None, ge=0)
    capacity: Optional[int] = Field(None, gt=0)
    price_per_night: Optional[Decimal] = Field(None, gt=0)
    status: Optional[str] = None
    is_active: Optional[bool] = None


class RoomResponse(BaseModel):
    id: int
    room_number: str
    room_type: str
    floor: int
    capacity: int
    price_per_night: Decimal
    status: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Backward compatibility with the older room router
RoomOut = RoomResponse
