from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)
from app.schemas.room import RoomOut
from app.services import reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    return reservation_service.create_reservation(db, payload)


# this must come BEFORE "/{reservation_id}", or FastAPI reads "availability" as an id
@router.get("/availability", response_model=list[RoomOut])
def check_availability(
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db),
):
    if check_out <= check_in:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Check-out must be after check-in")
    return reservation_service.available_rooms(db, check_in, check_out)


@router.get("", response_model=list[ReservationResponse])
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    guest_id: int | None = None,
    room_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(Reservation).order_by(Reservation.id)
    if guest_id:
        query = query.where(Reservation.guest_id == guest_id)
    if room_id:
        query = query.where(Reservation.room_id == room_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    return reservation


@router.patch("/{reservation_id}/status", response_model=ReservationResponse)
def update_status(
    reservation_id: int, payload: ReservationUpdate, db: Session = Depends(get_db)
):
    return reservation_service.change_status(db, reservation_id, payload.status)