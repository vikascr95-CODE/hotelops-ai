from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ReservationStatus = Literal[
    "pending", "confirmed", "cancelled", "checked_in", "checked_out"
]


class ReservationCreate(BaseModel):
    guest_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    check_in: date
    check_out: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("Check-out must be after check-in")
        return self


class ReservationUpdate(BaseModel):
    status: ReservationStatus


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: Decimal
    status: str
    created_at: datetime