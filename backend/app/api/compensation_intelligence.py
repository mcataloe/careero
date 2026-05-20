import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.compensation_intelligence import CompensationIntelligenceResponse
from app.services.compensation_intelligence import (
    CompensationIntelligenceSeedMissingError,
    CompensationIntelligenceService,
    CompensationIntelligenceWorkspaceNotFoundError,
)

router = APIRouter(prefix="/analytics/compensation", tags=["analytics"])


def get_compensation_intelligence_service(
    db: Session = Depends(get_db),
) -> CompensationIntelligenceService:
    return CompensationIntelligenceService(db)


@router.get("", response_model=CompensationIntelligenceResponse)
def get_compensation_intelligence(
    workspace_id: uuid.UUID | None = None,
    service: CompensationIntelligenceService = Depends(
        get_compensation_intelligence_service
    ),
):
    try:
        return service.get_compensation_intelligence(workspace_id=workspace_id)
    except CompensationIntelligenceWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompensationIntelligenceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
