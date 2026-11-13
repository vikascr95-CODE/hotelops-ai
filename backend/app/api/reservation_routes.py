
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
)
from app.schemas.room import RoomResponse
from app.services import reservation_service

router = APIRouter(tags=["Reservations"])


@router.post(
    "/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
):
    return reservation_service.create_reservation(db, reservation)


# Keep availability before the dynamic reservation ID route.
@router.get(
    "/reservations/availability",
    response_model=list[RoomResponse],
)
def get_available_rooms(
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db),
):
    if check_out <= check_in:
        raise HTTPException(
            status_code=422,
            detail="Check-out must be after check-in",
        )

    return reservation_service.available_rooms(
        db,
        check_in,
        check_out,
    )


@router.get(
    "/reservations/{reservation_id}",
    response_model=ReservationResponse,
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.get(Reservation, reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    return reservation


@router.patch(
    "/reservations/{reservation_id}/status",
    response_model=ReservationResponse,
)
def update_reservation_status(
    reservation_id: int,
    update: ReservationUpdate,
    db: Session = Depends(get_db),
):
    return reservation_service.change_status(
        db,
        reservation_id,
        update.status,
    )
