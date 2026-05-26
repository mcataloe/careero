from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai_usage import AIUsageListResponse
from app.services.ai_usage import (
    AIUsageSeedMissingError,
    AIUsageService,
    usage_note,
    usage_response,
    usage_summary,
)

router = APIRouter(prefix="/usage", tags=["usage"])


def get_ai_usage_service(db: Session = Depends(get_db)) -> AIUsageService:
    return AIUsageService(db)


@router.get("/ai", response_model=AIUsageListResponse)
def list_ai_usage(
    limit: int = Query(default=50, ge=1, le=200),
    service: AIUsageService = Depends(get_ai_usage_service),
) -> dict:
    try:
        events = service.list_recent(limit=limit)
    except AIUsageSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {
        "events": [usage_response(event) for event in events],
        "summary": usage_summary(events),
        "usage_note": usage_note(),
    }
