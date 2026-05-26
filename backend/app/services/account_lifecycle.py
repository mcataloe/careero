from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AccountLifecycleRequest, User
from app.schemas.account_lifecycle import AccountLifecycleRequestCreate
from app.services.activity_log import ActivityLogService
from app.services.current_user import (
    CurrentUserContext,
    CurrentUserResolutionError,
    get_current_user_context,
    resolve_current_user,
)


class AccountLifecycleSeedMissingError(Exception):
    pass


class AccountLifecycleRequestNotFoundError(Exception):
    pass


class AccountLifecycleRequestStateError(Exception):
    pass


class AccountLifecycleService:
    def __init__(
        self,
        db: Session,
        current_user_context: CurrentUserContext | None = None,
    ) -> None:
        self.db = db
        self.current_user_context = current_user_context or get_current_user_context()
        self.activity_log = ActivityLogService(db)

    def create_request(
        self,
        payload: AccountLifecycleRequestCreate,
    ) -> AccountLifecycleRequest:
        user = self._current_user()
        request = AccountLifecycleRequest(
            user_id=user.id,
            request_type=payload.request_type,
            status="requested",
            request_reason=payload.request_reason.strip()
            if payload.request_reason
            else None,
            target_type=payload.target_type.strip() if payload.target_type else None,
            target_id=payload.target_id,
            request_metadata=_safe_request_metadata(payload.request_metadata),
        )
        self.db.add(request)
        self.db.flush()
        self._log_lifecycle_event(
            user_id=user.id,
            request=request,
            action="account_lifecycle.requested",
        )
        self.db.commit()
        self.db.refresh(request)
        return request

    def list_requests(self) -> list[AccountLifecycleRequest]:
        user = self._current_user()
        statement = (
            select(AccountLifecycleRequest)
            .where(AccountLifecycleRequest.user_id == user.id)
            .order_by(
                AccountLifecycleRequest.requested_at.desc(),
                AccountLifecycleRequest.id.desc(),
            )
        )
        return list(self.db.scalars(statement))

    def cancel_request(self, request_id: uuid.UUID) -> AccountLifecycleRequest:
        user = self._current_user()
        request = self.db.scalar(
            select(AccountLifecycleRequest).where(
                AccountLifecycleRequest.id == request_id,
                AccountLifecycleRequest.user_id == user.id,
            )
        )
        if request is None:
            raise AccountLifecycleRequestNotFoundError("Lifecycle request not found")
        if request.status not in {"requested", "acknowledged"}:
            raise AccountLifecycleRequestStateError(
                "Only requested or acknowledged lifecycle requests can be canceled"
            )
        request.status = "canceled"
        request.canceled_at = datetime.now(timezone.utc)
        self._log_lifecycle_event(
            user_id=user.id,
            request=request,
            action="account_lifecycle.canceled",
        )
        self.db.commit()
        self.db.refresh(request)
        return request

    def _current_user(self) -> User:
        try:
            return resolve_current_user(self.db, self.current_user_context)
        except CurrentUserResolutionError as exc:
            raise AccountLifecycleSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def _log_lifecycle_event(
        self,
        *,
        user_id: uuid.UUID,
        request: AccountLifecycleRequest,
        action: str,
    ) -> None:
        self.activity_log.append(
            user_id=user_id,
            entity_type="account_lifecycle_request",
            entity_id=request.id,
            action=action,
            details={
                "request_type": request.request_type,
                "status": request.status,
                "target_type": request.target_type,
                "target_id": str(request.target_id) if request.target_id else None,
                "deletion_enforced": False,
            },
        )


def lifecycle_message(request: AccountLifecycleRequest) -> str:
    if request.request_type == "account_deletion":
        return (
            "Deletion request recorded locally. Data has not been deleted; "
            "deletion enforcement remains future."
        )
    if request.request_type == "data_export":
        return (
            "Export request recorded locally. Use the local data export panel "
            "to download JSON in this runtime."
        )
    return (
        "Lifecycle request recorded locally. No destructive data changes were performed."
    )


def lifecycle_note() -> str:
    return (
        "Local lifecycle requests are audit records only. They do not delete, "
        "anonymize, recover, or submit support work."
    )


def lifecycle_response(request: AccountLifecycleRequest) -> dict[str, Any]:
    return {
        "id": request.id,
        "user_id": request.user_id,
        "request_type": request.request_type,
        "status": request.status,
        "requested_at": request.requested_at,
        "acknowledged_at": request.acknowledged_at,
        "completed_at": request.completed_at,
        "canceled_at": request.canceled_at,
        "request_reason": request.request_reason,
        "target_type": request.target_type,
        "target_id": request.target_id,
        "request_metadata": request.request_metadata or {},
        "created_at": request.created_at,
        "updated_at": request.updated_at,
        "message": lifecycle_message(request),
    }


def _safe_request_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    allowed: dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            allowed[str(key)[:100]] = value
        elif isinstance(value, list):
            allowed[str(key)[:100]] = [
                item for item in value if isinstance(item, (str, int, float, bool))
            ][:20]
    return allowed
