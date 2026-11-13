
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationCreate(BaseModel):
    guest_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    check_in: datetime
    check_out: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("Check-out must be after check-in")
        return self


class ReservationUpdate(BaseModel):
    status: Literal[
        "pending",
        "confirmed",
        "cancelled",
        "checked_in",
        "checked_out",
    ]


class ReservationResponse(BaseModel):
    id: int
    guest_id: int
    room_id: int
    check_in: datetime
    check_out: datetime
    total_price: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
