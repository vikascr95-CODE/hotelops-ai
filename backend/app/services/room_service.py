
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate


def create_room(db: Session, room_data: RoomCreate):
    room = Room(**room_data.model_dump())

    try:
        db.add(room)
        db.commit()
        db.refresh(room)
        return room
    except IntegrityError:
        db.rollback()
        raise ValueError("Room number already exists")


def get_room(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()


def get_rooms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
):
    query = db.query(Room)

    if not include_inactive:
        query = query.filter(Room.is_active.is_(True))

    return query.order_by(Room.id).offset(skip).limit(limit).all()


def update_room(db: Session, room_id: int, room_data: RoomUpdate):
    room = get_room(db, room_id)

    if room is None:
        return None

    update_data = room_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(room, field, value)

    try:
        db.commit()
        db.refresh(room)
        return room
    except IntegrityError:
        db.rollback()
        raise ValueError("Room number already exists")


def delete_room(db: Session, room_id: int):
    room = get_room(db, room_id)

    if room is None:
        return None

    room.is_active = False
    db.commit()
    db.refresh(room)

    return room
