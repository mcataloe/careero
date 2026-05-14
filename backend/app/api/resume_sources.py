import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.resume_sources import (
    ActiveResumeSourceResponse,
    ResumeSourceCreate,
    ResumeSourceImportResponse,
    ResumeSourceResponse,
    ResumeSourceUpdate,
    ResumeSourceVersionCreate,
    ResumeSourceVersionResponse,
)
from app.services.resume_source_imports import (
    MAX_RESUME_SOURCE_IMPORT_BYTES,
    ResumeSourceImportTooLargeError,
    ResumeSourceImportUnreadableError,
    ResumeSourceImportUnsupportedTypeError,
    import_resume_source_file,
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


@router.post("/import", response_model=ResumeSourceImportResponse)
async def import_resume_source(file: UploadFile = File(...)):
    content = await _read_upload_content(file)
    try:
        return import_resume_source_file(
            file_name=file.filename,
            content_type=file.content_type,
            content=content,
        )
    except ResumeSourceImportUnsupportedTypeError as exc:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc))
    except ResumeSourceImportTooLargeError as exc:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(exc))
    except ResumeSourceImportUnreadableError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))


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


async def _read_upload_content(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total_bytes = 0

    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break

        total_bytes += len(chunk)
        if total_bytes > MAX_RESUME_SOURCE_IMPORT_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Resume/profile file must be 5 MB or smaller.",
            )

        chunks.append(chunk)

    return b"".join(chunks)


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
