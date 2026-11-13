from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Room).where(Room.room_number == payload.room_number))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Room number already exists")
    room = Room(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("", response_model=list[RoomOut])
def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = select(Room).order_by(Room.id)
    if not include_inactive:
        query = query.where(Room.is_active.is_(True))
    return db.scalars(query.offset(skip).limit(limit)).all()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if not room or not room.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    room.is_active = False  # soft delete keeps reservation history intact
    db.commit()