from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RoomStatus = Literal["available", "occupied", "cleaning", "maintenance"]


class RoomBase(BaseModel):
    room_number: str = Field(min_length=1, max_length=20)
    room_type: str = Field(min_length=1, max_length=50)
    floor: int = Field(ge=0)
    capacity: int = Field(default=2, ge=1)
    price_per_night: Decimal = Field(gt=0)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type: str | None = Field(default=None, min_length=1, max_length=50)
    floor: int | None = Field(default=None, ge=0)
    capacity: int | None = Field(default=None, ge=1)
    price_per_night: Decimal | None = Field(default=None, gt=0)
    status: RoomStatus | None = None
    is_active: bool | None = None


class RoomOut(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    is_active: bool
    created_at: datetime