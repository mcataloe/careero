import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search_health import SearchHealthResponse
from app.services.search_health import SearchHealthSeedMissingError, SearchHealthService

router = APIRouter(prefix="/analytics/search-health", tags=["analytics"])


def get_search_health_service(db: Session = Depends(get_db)) -> SearchHealthService:
    return SearchHealthService(db)


@router.get("", response_model=SearchHealthResponse)
def get_search_health(
    workspace_id: uuid.UUID | None = None,
    service: SearchHealthService = Depends(get_search_health_service),
):
    try:
        return service.get_search_health(workspace_id=workspace_id)
    except SearchHealthSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
