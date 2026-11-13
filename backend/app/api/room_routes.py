
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.services import room_service


router = APIRouter(tags=["Rooms"])


# CREATE ROOM
@router.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/api/v1/rooms/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
):
    try:
        return room_service.create_room(db, room)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# GET ALL ROOMS WITH PAGINATION
@router.get(
    "/rooms",
    response_model=list[RoomResponse],
)
@router.get(
    "/api/v1/rooms/",
    response_model=list[RoomResponse],
    include_in_schema=False,
)
def get_rooms(
    skip: int = 0,
    limit: int = 10,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Skip cannot be negative",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be between 1 and 100",
        )

    return room_service.get_rooms(
        db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )


# GET ROOM BY ID
@router.get(
    "/rooms/{room_id}",
    response_model=RoomResponse,
)
@router.get(
    "/api/v1/rooms/{room_id}",
    response_model=RoomResponse,
    include_in_schema=False,
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = room_service.get_room(db, room_id)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


# UPDATE ROOM
@router.patch(
    "/rooms/{room_id}",
    response_model=RoomResponse,
)
@router.patch(
    "/api/v1/rooms/{room_id}",
    response_model=RoomResponse,
    include_in_schema=False,
)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
):
    try:
        room = room_service.update_room(
            db,
            room_id,
            room_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


# SOFT DELETE ROOM
@router.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router.delete(
    "/api/v1/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
):
    deleted = room_service.delete_room(db, room_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return None
