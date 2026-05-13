import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.resume_sources import (
    ActiveResumeSourceResponse,
    ResumeSourceCreate,
    ResumeSourceResponse,
    ResumeSourceUpdate,
    ResumeSourceVersionCreate,
    ResumeSourceVersionResponse,
)
from app.services.resume_sources import (
    ActiveResumeSourceNotFoundError,
    ResumeSourceNotFoundError,
    ResumeSourceSeedMissingError,
    ResumeSourceService,
    ResumeSourceVersionNotFoundError,
)

router = APIRouter(prefix="/resume-sources", tags=["resume-sources"])


def get_resume_source_service(db: Session = Depends(get_db)) -> ResumeSourceService:
    return ResumeSourceService(db)


@router.post("", response_model=ResumeSourceResponse, status_code=status.HTTP_201_CREATED)
def create_resume_source(
    payload: ResumeSourceCreate,
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.create_source(payload)
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=list[ResumeSourceResponse])
def list_resume_sources(
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.list_sources()
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/active", response_model=ActiveResumeSourceResponse)
def get_active_resume_source(
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.get_active()
    except ActiveResumeSourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{source_id}", response_model=ResumeSourceResponse)
def update_resume_source(
    source_id: uuid.UUID,
    payload: ResumeSourceUpdate,
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.update_source(source_id, payload)
    except ResumeSourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/{source_id}/versions",
    response_model=ResumeSourceVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume_source_version(
    source_id: uuid.UUID,
    payload: ResumeSourceVersionCreate,
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.create_version(source_id, payload)
    except ResumeSourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/{source_id}/versions/{version_id}/activate",
    response_model=ResumeSourceVersionResponse,
)
def activate_resume_source_version(
    source_id: uuid.UUID,
    version_id: uuid.UUID,
    service: ResumeSourceService = Depends(get_resume_source_service),
):
    try:
        return service.activate_version(source_id, version_id)
    except (ResumeSourceNotFoundError, ResumeSourceVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ResumeSourceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
