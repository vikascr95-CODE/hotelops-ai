from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.triage import PRIORITY_ORDER, triage
from app.database.connection import get_db
from app.models.service_request import ServiceRequest
from app.schemas.service_request import ServiceRequestResponse
from app.schemas.triage import ApplyResponse, TriageRequest, TriageResult

router = APIRouter(prefix="/triage", tags=["AI Triage Agent"])


@router.post("/predict", response_model=TriageResult)
def predict(payload: TriageRequest):
    """Suggest a category, priority and team. Changes nothing."""
    return triage(payload.description)


@router.post("/service-requests/{request_id}/apply", response_model=ApplyResponse)
def apply_triage(request_id: int, db: Session = Depends(get_db)):
    """Let the agent update a real service request, with safety checks."""
    request = db.get(ServiceRequest, request_id)
    if not request:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service request not found")

    result = triage(request.description)

    def respond(applied: bool, message: str, changes: list[str]):
        return ApplyResponse(
            applied=applied,
            message=message,
            changes=changes,
            triage=result,
            service_request=ServiceRequestResponse.model_validate(request),
        )

    # Safety check 1: never touch a request that is already closed.
    if request.status in {"completed", "cancelled"}:
        return respond(False, "Request is closed, so triage was not applied.", [])

    # Safety check 2: when the model is unsure, hand over to a human.
    if result["needs_review"]:
        return respond(False, "Low confidence. A human should review this request.", [])

    changes = []
    if request.request_type != result["category"]:
        changes.append(f"request_type: {request.request_type} -> {result['category']}")
        request.request_type = result["category"]

    # Safety check 3: the agent may raise a priority, but never lower one.
    current = PRIORITY_ORDER.index(request.priority) if request.priority in PRIORITY_ORDER else 0
    suggested = PRIORITY_ORDER.index(result["priority"])
    if suggested > current:
        changes.append(f"priority: {request.priority} -> {result['priority']}")
        request.priority = result["priority"]

    if changes:
        db.commit()
        db.refresh(request)
    return respond(True, "Triage applied." if changes else "Nothing needed changing.", changes)