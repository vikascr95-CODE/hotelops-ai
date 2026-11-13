
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


def create_guest(db: Session, guest_data: GuestCreate) -> Guest:
    guest = Guest(**guest_data.model_dump())

    try:
        db.add(guest)
        db.commit()
        db.refresh(guest)
        return guest
    except IntegrityError:
        db.rollback()
        raise ValueError("A guest with this email already exists.")


def get_guest(db: Session, guest_id: int) -> Guest | None:
    return db.get(Guest, guest_id)


def get_guests(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Guest]:
    statement = (
        select(Guest)
        .order_by(Guest.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def update_guest(
    db: Session,
    guest: Guest,
    guest_data: GuestUpdate,
) -> Guest:
    updates = guest_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(guest, field, value)

    try:
        db.commit()
        db.refresh(guest)
        return guest
    except IntegrityError:
        db.rollback()
        raise ValueError("A guest with this email already exists.")


def delete_guest(db: Session, guest: Guest) -> None:
    db.delete(guest)
    db.commit()
