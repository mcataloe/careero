import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.account_lifecycle import (
    AccountLifecycleRequestCreate,
    AccountLifecycleRequestListResponse,
    AccountLifecycleRequestResponse,
)
from app.services.account_lifecycle import (
    AccountLifecycleRequestNotFoundError,
    AccountLifecycleRequestStateError,
    AccountLifecycleSeedMissingError,
    AccountLifecycleService,
    lifecycle_note,
    lifecycle_response,
)

router = APIRouter(prefix="/account/lifecycle-requests", tags=["account-lifecycle"])


def get_account_lifecycle_service(
    db: Session = Depends(get_db),
) -> AccountLifecycleService:
    return AccountLifecycleService(db)


@router.post(
    "",
    response_model=AccountLifecycleRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lifecycle_request(
    payload: AccountLifecycleRequestCreate,
    service: AccountLifecycleService = Depends(get_account_lifecycle_service),
) -> dict:
    try:
        request = service.create_request(payload)
    except AccountLifecycleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return lifecycle_response(request)


@router.get("", response_model=AccountLifecycleRequestListResponse)
def list_lifecycle_requests(
    service: AccountLifecycleService = Depends(get_account_lifecycle_service),
) -> dict:
    try:
        requests = service.list_requests()
    except AccountLifecycleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {
        "requests": [lifecycle_response(request) for request in requests],
        "lifecycle_note": lifecycle_note(),
    }


@router.post("/{request_id}/cancel", response_model=AccountLifecycleRequestResponse)
def cancel_lifecycle_request(
    request_id: uuid.UUID,
    service: AccountLifecycleService = Depends(get_account_lifecycle_service),
) -> dict:
    try:
        request = service.cancel_request(request_id)
    except AccountLifecycleRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AccountLifecycleRequestStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except AccountLifecycleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return lifecycle_response(request)
