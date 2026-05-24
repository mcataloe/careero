import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.artifact_exports import (
    ArtifactExportDependencyError,
    ArtifactExportNotFoundError,
    ArtifactExportSeedMissingError,
    ArtifactExportService,
    ArtifactExportValidationError,
)

router = APIRouter(prefix="/artifacts", tags=["artifact-exports"])


def get_artifact_export_service(db: Session = Depends(get_db)) -> ArtifactExportService:
    return ArtifactExportService(db)


@router.post("/{artifact_id}/exports/{export_format}")
def export_artifact(
    artifact_id: uuid.UUID,
    export_format: Literal["md", "docx", "pdf"],
    service: ArtifactExportService = Depends(get_artifact_export_service),
):
    try:
        result = service.export_artifact(
            artifact_id=artifact_id,
            export_format=export_format,
        )
    except ArtifactExportNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ArtifactExportSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ArtifactExportDependencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except ArtifactExportValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    headers = {
        "Content-Disposition": f'attachment; filename="{result.file_name}"',
        "X-Careero-Content-Hash": result.content_hash,
    }
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers=headers,
    )
