import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.automation import (
    AutomationApprovalLogListResponse,
    AutomationApprovalLogResponse,
    AutomationDecisionRequest,
    AutomationPreferencesResponse,
    AutomationPreferencesUpdate,
    AutomationSuggestionListResponse,
)
from app.services.automation import (
    AutomationNotFoundError,
    AutomationSeedMissingError,
    AutomationService,
    AutomationValidationError,
    AutomationWorkspaceNotFoundError,
)

router = APIRouter(tags=["automation"])


def get_automation_service(db: Session = Depends(get_db)) -> AutomationService:
    return AutomationService(db)


@router.get("/automation/suggestions", response_model=AutomationSuggestionListResponse)
def list_automation_suggestions(
    workspace_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: uuid.UUID | None = None,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.list_suggestions(
            workspace_id=workspace_id,
            target_type=target_type,
            target_id=target_id,
        )
    except AutomationWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/automation/suggestions/{suggestion_id}/approve",
    response_model=AutomationApprovalLogResponse,
)
def approve_automation_suggestion(
    suggestion_id: uuid.UUID,
    payload: AutomationDecisionRequest | None = None,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.approve_suggestion(
            suggestion_id,
            actor=payload.actor if payload else "user",
        )
    except AutomationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/automation/suggestions/{suggestion_id}/reject",
    response_model=AutomationApprovalLogResponse,
)
def reject_automation_suggestion(
    suggestion_id: uuid.UUID,
    payload: AutomationDecisionRequest | None = None,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.reject_suggestion(
            suggestion_id,
            reason=payload.reason if payload else None,
            actor=payload.actor if payload else "user",
        )
    except AutomationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/automation/suggestions/{suggestion_id}/dismiss",
    response_model=AutomationApprovalLogResponse,
)
def dismiss_automation_suggestion(
    suggestion_id: uuid.UUID,
    payload: AutomationDecisionRequest | None = None,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.dismiss_suggestion(
            suggestion_id,
            reason=payload.reason if payload else None,
            actor=payload.actor if payload else "user",
        )
    except AutomationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/automation/approval-logs", response_model=AutomationApprovalLogListResponse)
def list_automation_approval_logs(
    workspace_id: uuid.UUID | None = None,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.list_approval_logs(workspace_id=workspace_id)
    except AutomationWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/automation-preferences",
    response_model=AutomationPreferencesResponse,
)
def get_workspace_automation_preferences(
    workspace_id: uuid.UUID,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.get_preferences(workspace_id)
    except AutomationWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/workspaces/{workspace_id}/automation-preferences",
    response_model=AutomationPreferencesResponse,
)
def update_workspace_automation_preferences(
    workspace_id: uuid.UUID,
    payload: AutomationPreferencesUpdate,
    service: AutomationService = Depends(get_automation_service),
):
    try:
        return service.update_preferences(workspace_id, payload)
    except AutomationWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AutomationValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except AutomationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
