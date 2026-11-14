
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.models.room import Room
from app.models.reservation import Reservation
from app.models.service_request import ServiceRequest
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate


ALLOWED_TRANSITIONS = {
    "pending": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def create_service_request(db: Session, data: ServiceRequestCreate):
    guest = db.get(Guest, data.guest_id)
    if not guest:
        raise ValueError("Guest not found")

    room = db.get(Room, data.room_id)
    if not room:
        raise ValueError("Room not found")

    if data.reservation_id is not None:
        reservation = db.get(Reservation, data.reservation_id)

        if not reservation:
            raise ValueError("Reservation not found")

        if reservation.guest_id != data.guest_id:
            raise ValueError("Reservation does not belong to this guest")

        if reservation.room_id != data.room_id:
            raise ValueError("Reservation does not belong to this room")

    request = ServiceRequest(**data.model_dump())

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_service_request(db: Session, request_id: int):
    request = db.get(ServiceRequest, request_id)

    if not request:
        raise ValueError("Service request not found")

    return request


def list_service_requests(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    priority: str | None = None,
):
    query = select(ServiceRequest)

    if status:
        query = query.where(ServiceRequest.status == status)

    if priority:
        query = query.where(ServiceRequest.priority == priority)

    query = query.order_by(ServiceRequest.created_at.desc())
    query = query.offset(skip).limit(limit)

    return db.scalars(query).all()


def update_service_request(
    db: Session,
    request_id: int,
    data: ServiceRequestUpdate,
):
    request = get_service_request(db, request_id)

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)

    return request


def change_service_request_status(
    db: Session,
    request_id: int,
    new_status: str,
):
    request = get_service_request(db, request_id)

    allowed = ALLOWED_TRANSITIONS.get(request.status, set())

    if new_status not in allowed:
        raise ValueError(
            f"Cannot change status from '{request.status}' to '{new_status}'"
        )

    request.status = new_status

    db.commit()
    db.refresh(request)

    return request


def delete_service_request(db: Session, request_id: int):
    request = get_service_request(db, request_id)

    db.delete(request)
    db.commit()

    return True
