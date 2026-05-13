import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.activity_log import ActivityLogResponse
from app.services.activity_log import ActivityLogSeedMissingError, ActivityLogService

router = APIRouter(tags=["activity-log"])


def get_activity_log_service(db: Session = Depends(get_db)) -> ActivityLogService:
    return ActivityLogService(db)


@router.get("/activity-log", response_model=list[ActivityLogResponse])
def list_activity_log(
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    action: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    service: ActivityLogService = Depends(get_activity_log_service),
):
    try:
        return service.list_for_default_user(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            limit=limit,
        )
    except ActivityLogSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
