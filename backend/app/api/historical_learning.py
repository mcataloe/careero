import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.historical_learning import HistoricalLearningResponse
from app.services.historical_learning import (
    HistoricalLearningSeedMissingError,
    HistoricalLearningService,
)

router = APIRouter(prefix="/analytics/history", tags=["analytics"])


def get_historical_learning_service(
    db: Session = Depends(get_db),
) -> HistoricalLearningService:
    return HistoricalLearningService(db)


@router.get("", response_model=HistoricalLearningResponse)
def get_historical_learning(
    workspace_id: uuid.UUID | None = None,
    service: HistoricalLearningService = Depends(get_historical_learning_service),
):
    try:
        return service.get_historical_learning(workspace_id=workspace_id)
    except HistoricalLearningSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
