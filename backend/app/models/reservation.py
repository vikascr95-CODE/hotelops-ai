
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    guest_id: Mapped[int] = mapped_column(
        ForeignKey("guests.id"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"), nullable=False
    )

    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="confirmed"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="reservations")
    room: Mapped["Room"] = relationship(back_populates="reservations")
    service_requests: Mapped[list["ServiceRequest"]] = relationship(
        back_populates="reservation"
    )
