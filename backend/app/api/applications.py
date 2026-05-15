import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.applications import (
    ApplicationDetailResponse,
    ApplicationListItemResponse,
    ApplicationMetadataUpdate,
    ApplicationStateTransitionRequest,
)
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowSeedMissingError,
    ApplicationWorkflowService,
    ApplicationWorkflowValidationError,
    ApplicationWorkflowWorkspaceInactiveError,
    ApplicationWorkflowWorkspaceNotFoundError,
)

router = APIRouter(tags=["applications"])


def get_application_workflow_service(
    db: Session = Depends(get_db),
) -> ApplicationWorkflowService:
    return ApplicationWorkflowService(db)


@router.post(
    "/roles/{role_id}/application",
    response_model=ApplicationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def get_or_create_role_application(
    role_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_or_create_for_role(role_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications", response_model=list[ApplicationListItemResponse])
def list_applications(
    workspace_id: uuid.UUID | None = None,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_applications(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/applications",
    response_model=list[ApplicationListItemResponse],
)
def list_workspace_applications(
    workspace_id: uuid.UUID,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_applications(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
def get_application(
    application_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_application(application_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/applications/{application_id}", response_model=ApplicationDetailResponse)
def update_application(
    application_id: uuid.UUID,
    payload: ApplicationMetadataUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.update_application(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/state-transitions",
    response_model=ApplicationDetailResponse,
)
def transition_application_state(
    application_id: uuid.UUID,
    payload: ApplicationStateTransitionRequest,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.transition_state(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
