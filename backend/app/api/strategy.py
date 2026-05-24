import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.strategy import CareerStrategySummary, SearchTrackStrategySummary
from app.services.strategy import (
    CareerStrategySeedMissingError,
    CareerStrategyService,
    CareerStrategyWorkspaceNotFoundError,
)

router = APIRouter(prefix="/strategy", tags=["strategy"])


def get_career_strategy_service(
    db: Session = Depends(get_db),
) -> CareerStrategyService:
    return CareerStrategyService(db)


@router.get("/workspaces/{workspace_id}", response_model=SearchTrackStrategySummary)
def get_workspace_strategy(
    workspace_id: uuid.UUID,
    service: CareerStrategyService = Depends(get_career_strategy_service),
):
    try:
        return service.get_workspace_strategy(workspace_id=workspace_id)
    except CareerStrategyWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CareerStrategySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/workspaces", response_model=CareerStrategySummary)
def list_workspace_strategy(
    include_cross_track: bool = False,
    service: CareerStrategyService = Depends(get_career_strategy_service),
):
    try:
        return service.get_career_strategy(include_cross_track=include_cross_track)
    except CareerStrategySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
