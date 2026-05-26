import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActivityLog, User
from app.services.current_user import CurrentUserResolutionError, resolve_current_user


class ActivityLogSeedMissingError(Exception):
    pass


class ActivityLogService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise ActivityLogSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def append(
        self,
        *,
        user_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> ActivityLog:
        entry = ActivityLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            details=details or {},
        )
        self.db.add(entry)
        return entry

    def list_for_default_user(
        self,
        *,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        action: str | None = None,
        limit: int = 50,
    ) -> list[ActivityLog]:
        user = self.get_default_user()
        filters = [ActivityLog.user_id == user.id]
        if entity_type is not None:
            filters.append(ActivityLog.entity_type == entity_type)
        if entity_id is not None:
            filters.append(ActivityLog.entity_id == entity_id)
        if action is not None:
            filters.append(ActivityLog.action == action)

        statement = (
            select(ActivityLog)
            .where(*filters)
            .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement))
