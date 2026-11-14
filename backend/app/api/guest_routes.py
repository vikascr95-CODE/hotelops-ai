
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.services import guest_service

router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)


@router.post(
    "",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guest(
    guest_data: GuestCreate,
    db: Session = Depends(get_db),
):
    try:
        return guest_service.create_guest(db, guest_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get("", response_model=list[GuestResponse])
def list_guests(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return guest_service.get_guests(db, skip=skip, limit=limit)


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
):
    guest = guest_service.get_guest(db, guest_id)

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found.",
        )

    return guest


@router.patch("/{guest_id}", response_model=GuestResponse)
def update_guest(
    guest_id: int,
    guest_data: GuestUpdate,
    db: Session = Depends(get_db),
):
    guest = guest_service.get_guest(db, guest_id)

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found.",
        )

    try:
        return guest_service.update_guest(db, guest, guest_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.delete(
    "/{guest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_guest(
    guest_id: int,
    db: Session = Depends(get_db),
):
    guest = guest_service.get_guest(db, guest_id)

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found.",
        )

    try:
        guest_service.delete_guest(db, guest)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Guest cannot be deleted because related records exist.",
        )
