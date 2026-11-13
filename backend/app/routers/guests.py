from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.guest import Guest
from app.models.reservation import Reservation
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate

router = APIRouter(prefix="/guests", tags=["guests"])


@router.post("", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(payload: GuestCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Guest).where(Guest.email == payload.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "A guest with this email already exists")
    guest = Guest(**payload.model_dump())
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


@router.get("", response_model=list[GuestResponse])
def list_guests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return db.scalars(select(Guest).order_by(Guest.id).offset(skip).limit(limit)).all()


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guest not found")
    return guest


@router.patch("/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, payload: GuestUpdate, db: Session = Depends(get_db)):
    guest = db.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guest not found")

    changes = payload.model_dump(exclude_unset=True)
    new_email = changes.get("email")
    if new_email and new_email != guest.email:
        taken = db.scalar(select(Guest).where(Guest.email == new_email))
        if taken:
            raise HTTPException(status.HTTP_409_CONFLICT, "A guest with this email already exists")

    for field, value in changes.items():
        setattr(guest, field, value)
    db.commit()
    db.refresh(guest)
    return guest


@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guest not found")
    has_bookings = db.scalar(select(Reservation.id).where(Reservation.guest_id == guest_id))
    if has_bookings:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Guest has reservations and cannot be deleted"
        )
    db.delete(guest)
    db.commit()