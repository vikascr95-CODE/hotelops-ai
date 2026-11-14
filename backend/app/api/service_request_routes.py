from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestStatusUpdate,
    ServiceRequestResponse,
)
from app.services import service_request_service


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests"],
)


@router.post(
    "/",
    response_model=ServiceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    data: ServiceRequestCreate,
    db: Session = Depends(get_db),
):
    try:
        return service_request_service.create_service_request(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/", response_model=list[ServiceRequestResponse])
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    request_status: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return service_request_service.list_service_requests(
        db,
        skip=skip,
        limit=limit,
        status=request_status,
        priority=priority,
    )


@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service_request_service.get_service_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{request_id}", response_model=ServiceRequestResponse)
def update_request(
    request_id: int,
    data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service_request_service.update_service_request(
            db, request_id, data
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch(
    "/{request_id}/status",
    response_model=ServiceRequestResponse,
)
def update_request_status(
    request_id: int,
    data: ServiceRequestStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service_request_service.change_service_request_status(
            db, request_id, data.status
        )
    except ValueError as exc:
        message = str(exc)
        code = 404 if message == "Service request not found" else 409
        raise HTTPException(status_code=code, detail=message)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    try:
        service_request_service.delete_service_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
