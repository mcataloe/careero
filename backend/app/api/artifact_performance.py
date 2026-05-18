import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.artifact_performance import ArtifactPerformanceResponse
from app.services.artifact_performance import (
    ArtifactPerformanceSeedMissingError,
    ArtifactPerformanceService,
)

router = APIRouter(prefix="/analytics/artifacts", tags=["analytics"])


def get_artifact_performance_service(
    db: Session = Depends(get_db),
) -> ArtifactPerformanceService:
    return ArtifactPerformanceService(db)


@router.get("", response_model=ArtifactPerformanceResponse)
def get_artifact_performance(
    workspace_id: uuid.UUID | None = None,
    service: ArtifactPerformanceService = Depends(get_artifact_performance_service),
):
    try:
        return service.get_performance(workspace_id=workspace_id)
    except ArtifactPerformanceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
