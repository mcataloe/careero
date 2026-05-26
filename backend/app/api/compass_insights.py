import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.compass_insights import CompassInsightsResponse
from app.services.compass_insights import (
    CompassInsightsSeedMissingError,
    CompassInsightsService,
    CompassInsightsWorkspaceNotFoundError,
)

router = APIRouter(prefix="/analytics/compass", tags=["analytics"])


def get_compass_insights_service(
    db: Session = Depends(get_db),
) -> CompassInsightsService:
    return CompassInsightsService(db)


@router.get("", response_model=CompassInsightsResponse)
def get_compass_insights(
    workspace_id: uuid.UUID | None = None,
    service: CompassInsightsService = Depends(get_compass_insights_service),
):
    try:
        return service.get_compass_insights(workspace_id=workspace_id)
    except CompassInsightsWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompassInsightsSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
