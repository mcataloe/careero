import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stride_insights import StrideInsightsResponse
from app.services.stride_insights import (
    StrideInsightsSeedMissingError,
    StrideInsightsService,
    StrideInsightsWorkspaceNotFoundError,
)

router = APIRouter(prefix="/analytics/stride", tags=["analytics"])


def get_stride_insights_service(
    db: Session = Depends(get_db),
) -> StrideInsightsService:
    return StrideInsightsService(db)


@router.get("", response_model=StrideInsightsResponse)
def get_stride_insights(
    workspace_id: uuid.UUID | None = None,
    service: StrideInsightsService = Depends(get_stride_insights_service),
):
    try:
        return service.get_stride_insights(workspace_id=workspace_id)
    except StrideInsightsWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except StrideInsightsSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
