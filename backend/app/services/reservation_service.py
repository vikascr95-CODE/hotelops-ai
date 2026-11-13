from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.models.reservation import Reservation
from app.models.room import Room
from app.schemas.reservation import ReservationCreate

# which status changes are allowed from each current status
ALLOWED_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"checked_in", "cancelled"},
    "checked_in": {"checked_out"},
    "checked_out": set(),
    "cancelled": set(),
}


def find_overlapping(db: Session, room_id: int, check_in: date, check_out: date):
    """Return a reservation for this room whose dates collide with the given dates.
    Check-out day is free, so a stay ending on the 12th and one starting on
    the 12th do not collide. Cancelled bookings are ignored."""
    query = select(Reservation).where(
        Reservation.room_id == room_id,
        Reservation.status != "cancelled",
        Reservation.check_in < check_out,
        Reservation.check_out > check_in,
    )
    return db.scalars(query).first()


def create_reservation(db: Session, data: ReservationCreate) -> Reservation:
    if data.check_in < date.today():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Check-in cannot be in the past")

    if not db.get(Guest, data.guest_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guest not found")

    room = db.get(Room, data.room_id)
    if not room or not room.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    if room.status == "maintenance":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Room is under maintenance")

    if find_overlapping(db, data.room_id, data.check_in, data.check_out):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Room is already booked for these dates"
        )

    nights = (data.check_out - data.check_in).days
    reservation = Reservation(
        guest_id=data.guest_id,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out,
        total_price=room.price_per_night * nights,
        status="confirmed",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def change_status(db: Session, reservation_id: int, new_status: str) -> Reservation:
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")

    allowed = ALLOWED_TRANSITIONS.get(reservation.status, set())
    if new_status not in allowed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Cannot change status from '{reservation.status}' to '{new_status}'",
        )

    reservation.status = new_status

    # keep the room's status in step with the guest's stay
    room = db.get(Room, reservation.room_id)
    if new_status == "checked_in":
        room.status = "occupied"
    elif new_status == "checked_out":
        room.status = "cleaning"

    db.commit()
    db.refresh(reservation)
    return reservation


def available_rooms(db: Session, check_in: date, check_out: date):
    busy_room_ids = select(Reservation.room_id).where(
        Reservation.status != "cancelled",
        Reservation.check_in < check_out,
        Reservation.check_out > check_in,
    )
    query = (
        select(Room)
        .where(
            Room.is_active.is_(True),
            Room.status != "maintenance",
            Room.id.not_in(busy_room_ids),
        )
        .order_by(Room.room_number)
    )
    return db.scalars(query).all()