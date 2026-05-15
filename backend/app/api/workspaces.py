import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workspaces import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.services.workspaces import (
    WorkspaceInactiveError,
    WorkspaceNotFoundError,
    WorkspaceSeedMissingError,
    WorkspaceService,
    serialize_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def get_workspace_service(db: Session = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(db)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return serialize_workspace(service.create_workspace(payload))
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    include_inactive: bool = False,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return [
            serialize_workspace(workspace)
            for workspace in service.list_workspaces(
                include_inactive=include_inactive,
            )
        ]
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: uuid.UUID,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return serialize_workspace(
            service.get_by_id(workspace_id, include_inactive=True)
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: uuid.UUID,
    payload: WorkspaceUpdate,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return serialize_workspace(service.update_workspace(workspace_id, payload))
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{workspace_id}/archive", response_model=WorkspaceResponse)
def archive_workspace(
    workspace_id: uuid.UUID,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return serialize_workspace(service.archive_workspace(workspace_id))
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{workspace_id}/reactivate", response_model=WorkspaceResponse)
def reactivate_workspace(
    workspace_id: uuid.UUID,
    service: WorkspaceService = Depends(get_workspace_service),
):
    try:
        return serialize_workspace(service.reactivate_workspace(workspace_id))
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except WorkspaceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except WorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
