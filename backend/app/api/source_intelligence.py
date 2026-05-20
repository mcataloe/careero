import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.source_intelligence import SourceIntelligenceResponse
from app.services.source_intelligence import (
    SourceIntelligenceSeedMissingError,
    SourceIntelligenceService,
)

router = APIRouter(prefix="/analytics/sources", tags=["analytics"])


def get_source_intelligence_service(
    db: Session = Depends(get_db),
) -> SourceIntelligenceService:
    return SourceIntelligenceService(db)


@router.get("", response_model=SourceIntelligenceResponse)
def get_source_intelligence(
    workspace_id: uuid.UUID | None = None,
    service: SourceIntelligenceService = Depends(get_source_intelligence_service),
):
    try:
        return service.get_source_intelligence(workspace_id=workspace_id)
    except SourceIntelligenceSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
