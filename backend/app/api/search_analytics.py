import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search_analytics import SearchAnalyticsResponse
from app.services.search_analytics import (
    SearchAnalyticsSeedMissingError,
    SearchAnalyticsService,
    SearchAnalyticsWorkspaceNotFoundError,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_search_analytics_service(
    db: Session = Depends(get_db),
) -> SearchAnalyticsService:
    return SearchAnalyticsService(db)


@router.get("/search", response_model=SearchAnalyticsResponse)
def get_search_analytics(
    workspace_id: uuid.UUID | None = None,
    service: SearchAnalyticsService = Depends(get_search_analytics_service),
):
    try:
        return service.get_search_analytics(workspace_id=workspace_id)
    except SearchAnalyticsWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except SearchAnalyticsSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
