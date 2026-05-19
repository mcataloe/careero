import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendations import RecommendationListResponse
from app.services.recommendations import (
    RecommendationSeedMissingError,
    RecommendationService,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_recommendation_service(
    db: Session = Depends(get_db),
) -> RecommendationService:
    return RecommendationService(db)


@router.get("", response_model=RecommendationListResponse)
def list_recommendations(
    workspace_id: uuid.UUID | None = None,
    service: RecommendationService = Depends(get_recommendation_service),
):
    try:
        return service.list_recommendations(workspace_id=workspace_id)
    except RecommendationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
