import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.artifacts import (
    ArtifactDraftCreate,
    ArtifactDraftUpdate,
    ArtifactResponse,
)
from app.services.artifacts import (
    ArtifactNotFoundError,
    ArtifactSeedMissingError,
    ArtifactService,
    ArtifactTransitionError,
    ArtifactValidationError,
    ArtifactWorkspaceInactiveError,
    ArtifactWorkspaceNotFoundError,
)

router = APIRouter(tags=["artifacts"])


def get_artifact_service(db: Session = Depends(get_db)) -> ArtifactService:
    return ArtifactService(db)


@router.post("/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
def create_artifact_draft(
    payload: ArtifactDraftCreate,
    service: ArtifactService = Depends(get_artifact_service),
):
    try:
        return service.create_draft(payload)
    except ArtifactWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except ArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/artifacts", response_model=list[ArtifactResponse])
def list_artifacts(
    workspace_id: uuid.UUID | None = None,
    opportunity_id: uuid.UUID | None = None,
    application_id: uuid.UUID | None = None,
    include_archived: bool = False,
    service: ArtifactService = Depends(get_artifact_service),
):
    try:
        return service.list_artifacts(
            workspace_id=workspace_id,
            opportunity_id=opportunity_id,
            application_id=application_id,
            include_archived=include_archived,
        )
    except (ArtifactWorkspaceNotFoundError, ArtifactNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/opportunities/{opportunity_id}/artifacts", response_model=list[ArtifactResponse])
def list_opportunity_artifacts(
    opportunity_id: uuid.UUID,
    include_archived: bool = False,
    service: ArtifactService = Depends(get_artifact_service),
):
    return list_artifacts(
        opportunity_id=opportunity_id,
        include_archived=include_archived,
        service=service,
    )


@router.get("/workspaces/{workspace_id}/artifacts", response_model=list[ArtifactResponse])
def list_workspace_artifacts(
    workspace_id: uuid.UUID,
    include_archived: bool = False,
    service: ArtifactService = Depends(get_artifact_service),
):
    return list_artifacts(
        workspace_id=workspace_id,
        include_archived=include_archived,
        service=service,
    )


@router.get("/applications/{application_id}/artifacts", response_model=list[ArtifactResponse])
def list_application_artifacts(
    application_id: uuid.UUID,
    include_archived: bool = False,
    service: ArtifactService = Depends(get_artifact_service),
):
    return list_artifacts(
        application_id=application_id,
        include_archived=include_archived,
        service=service,
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    try:
        return service.get_artifact(artifact_id)
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def update_artifact_draft(
    artifact_id: uuid.UUID,
    payload: ArtifactDraftUpdate,
    service: ArtifactService = Depends(get_artifact_service),
):
    try:
        return service.update_draft(artifact_id, payload)
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/artifacts/{artifact_id}/mark-reviewed", response_model=ArtifactResponse)
def mark_artifact_reviewed(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    return _transition_response(lambda: service.mark_reviewed(artifact_id))


@router.post("/artifacts/{artifact_id}/review", response_model=ArtifactResponse)
def review_artifact(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    return _transition_response(lambda: service.mark_reviewed(artifact_id))


@router.post("/artifacts/{artifact_id}/mark-submitted", response_model=ArtifactResponse)
def mark_artifact_submitted(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    return _transition_response(lambda: service.mark_submitted(artifact_id))


@router.post("/artifacts/{artifact_id}/submit", response_model=ArtifactResponse)
def submit_artifact(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    return _transition_response(lambda: service.mark_submitted(artifact_id))


@router.post("/artifacts/{artifact_id}/archive", response_model=ArtifactResponse)
def archive_artifact(
    artifact_id: uuid.UUID,
    service: ArtifactService = Depends(get_artifact_service),
):
    return _transition_response(lambda: service.archive(artifact_id))


def _transition_response(callback):
    try:
        return callback()
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
