from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import WorkspaceStatus
from app.models import User, Workspace
from app.schemas.workspaces import WorkspaceCreate, WorkspaceUpdate
from app.seed import DEFAULT_WORKSPACE_ID
from app.services.activity_log import ActivityLogService
from app.services.current_user import (
    CurrentUserContext,
    CurrentUserResolutionError,
    get_current_user_context,
    resolve_current_user,
)
from app.services.ownership import (
    require_active_user_workspace_for_new_work,
    require_user_workspace,
)
from app.services.workspace_context import is_workspace_active_for_new_work


class WorkspaceError(Exception):
    pass


class WorkspaceSeedMissingError(WorkspaceError):
    pass


class WorkspaceNotFoundError(WorkspaceError):
    pass


class WorkspaceInactiveError(WorkspaceError):
    pass


class WorkspaceService:
    def __init__(
        self,
        db: Session,
        current_user_context: CurrentUserContext | None = None,
    ) -> None:
        self.db = db
        self.current_user_context = current_user_context or get_current_user_context()
        self.activity_log = ActivityLogService(db)

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db, self.current_user_context)
        except CurrentUserResolutionError as exc:
            raise WorkspaceSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def create_workspace(self, payload: WorkspaceCreate) -> Workspace:
        user = self.get_default_user()
        workspace = Workspace(
            user_id=user.id,
            title=payload.title.strip(),
            description=payload.description,
            workspace_type=payload.workspace_type.value,
            status=payload.status.value,
            preferences=_preferences_payload(payload.preferences),
            ai_context_summary=payload.ai_context_summary,
            tags=payload.tags,
            workspace_metadata=payload.metadata,
            archived_at=(
                datetime.now(timezone.utc)
                if payload.status == WorkspaceStatus.ARCHIVED
                else None
            ),
        )
        self.db.add(workspace)
        self.db.flush()
        self._log_activity(
            user_id=user.id,
            entity_id=workspace.id,
            action="workspace.created",
            details={"status": workspace.status},
        )
        self.db.commit()
        return self.get_by_id(workspace.id, include_inactive=True)

    def list_workspaces(self, *, include_inactive: bool = False) -> list[Workspace]:
        user = self.get_default_user()
        filters = [Workspace.user_id == user.id]
        if not include_inactive:
            filters.extend(
                [
                    Workspace.archived_at.is_(None),
                    Workspace.status.in_(["active", "paused"]),
                ]
            )
        statement = (
            select(Workspace)
            .where(*filters)
            .order_by(Workspace.created_at.asc(), Workspace.id.asc())
        )
        return list(self.db.scalars(statement))

    def get_by_id(
        self,
        workspace_id: uuid.UUID,
        *,
        include_inactive: bool = False,
    ) -> Workspace:
        user = self.get_default_user()
        return require_user_workspace(
            self.db,
            workspace_id=workspace_id,
            user_id=user.id,
            include_inactive=include_inactive,
            error_cls=WorkspaceNotFoundError,
            error_message="Workspace not found",
        )

    def update_workspace(
        self,
        workspace_id: uuid.UUID,
        payload: WorkspaceUpdate,
    ) -> Workspace:
        user = self.get_default_user()
        workspace = require_user_workspace(
            self.db,
            workspace_id=workspace_id,
            user_id=user.id,
            include_inactive=True,
            error_cls=WorkspaceNotFoundError,
            error_message="Workspace not found",
        )

        updates = payload.model_dump(exclude_unset=True)
        changed_fields: list[str] = []
        for field_name, value in updates.items():
            if field_name == "workspace_type" and value is not None:
                value = value.value
            elif field_name == "status" and value is not None:
                value = value.value
                if value == "archived" and workspace.archived_at is None:
                    workspace.archived_at = datetime.now(timezone.utc)
                elif value != "archived":
                    workspace.archived_at = None
            elif field_name == "preferences" and value is not None:
                value = _preferences_payload(payload.preferences)
            elif field_name == "metadata":
                field_name = "workspace_metadata"

            if getattr(workspace, field_name) != value:
                setattr(workspace, field_name, value)
                changed_fields.append(field_name)

        if changed_fields:
            self._log_activity(
                user_id=user.id,
                entity_id=workspace.id,
                action="workspace.updated",
                details={"changed_fields": sorted(changed_fields)},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return self.get_by_id(workspace.id, include_inactive=True)

    def archive_workspace(self, workspace_id: uuid.UUID) -> Workspace:
        user = self.get_default_user()
        workspace = require_user_workspace(
            self.db,
            workspace_id=workspace_id,
            user_id=user.id,
            include_inactive=True,
            error_cls=WorkspaceNotFoundError,
            error_message="Workspace not found",
        )
        workspace.status = "archived"
        workspace.archived_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=user.id,
            entity_id=workspace.id,
            action="workspace.archived",
            details={},
        )
        self.db.commit()
        return self.get_by_id(workspace.id, include_inactive=True)

    def reactivate_workspace(self, workspace_id: uuid.UUID) -> Workspace:
        user = self.get_default_user()
        workspace = require_user_workspace(
            self.db,
            workspace_id=workspace_id,
            user_id=user.id,
            include_inactive=True,
            error_cls=WorkspaceNotFoundError,
            error_message="Workspace not found",
        )
        workspace.status = "active"
        workspace.archived_at = None
        self._log_activity(
            user_id=user.id,
            entity_id=workspace.id,
            action="workspace.reactivated",
            details={},
        )
        self.db.commit()
        return self.get_by_id(workspace.id)

    def get_default_active_workspace(self, *, user_id: uuid.UUID) -> Workspace:
        workspace = self.db.get(Workspace, DEFAULT_WORKSPACE_ID)
        if (
            workspace is not None
            and workspace.user_id == user_id
            and is_workspace_active_for_new_work(workspace)
        ):
            return workspace

        workspace = self.db.scalar(
            select(Workspace)
            .where(
                Workspace.user_id == user_id,
                Workspace.archived_at.is_(None),
                Workspace.status.in_(["active", "paused"]),
            )
            .order_by(Workspace.created_at.asc(), Workspace.id.asc())
            .limit(1)
        )
        if workspace is None:
            raise WorkspaceInactiveError("No active workspace is available")
        return workspace

    def resolve_active_workspace(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> Workspace:
        if workspace_id is None:
            return self.get_default_active_workspace(user_id=user_id)

        return require_active_user_workspace_for_new_work(
            self.db,
            workspace_id=workspace_id,
            user_id=user_id,
            not_found_error_cls=WorkspaceNotFoundError,
            inactive_error_cls=WorkspaceInactiveError,
            not_found_message="Workspace not found",
            inactive_message="Workspace is not active",
        )

    def _log_activity(
        self,
        *,
        user_id: uuid.UUID,
        entity_id: uuid.UUID,
        action: str,
        details: dict[str, Any],
    ) -> None:
        self.activity_log.append(
            user_id=user_id,
            entity_type="workspace",
            entity_id=entity_id,
            action=action,
            details=details,
        )


def serialize_workspace(workspace: Workspace) -> dict[str, Any]:
    return {
        "id": workspace.id,
        "user_id": workspace.user_id,
        "title": workspace.title,
        "description": workspace.description,
        "workspace_type": workspace.workspace_type,
        "status": workspace.status,
        "preferences": workspace.preferences or {},
        "ai_context_summary": workspace.ai_context_summary,
        "tags": workspace.tags or [],
        "metadata": workspace.workspace_metadata or {},
        "archived_at": workspace.archived_at,
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at,
    }


def _preferences_payload(preferences: Any) -> dict[str, Any]:
    if preferences is None:
        return {}
    if hasattr(preferences, "model_dump"):
        return preferences.model_dump(mode="json")
    return dict(preferences)
