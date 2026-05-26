from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.interfaces import ORMOption

from app.constants import RoleStatus
from app.models import Application, Role, Workspace
from app.services.workspace_context import is_workspace_active_for_new_work


class OwnershipBoundaryNotFoundError(Exception):
    pass


TError = TypeVar("TError", bound=Exception)


def require_user_workspace(
    db: Session,
    *,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    include_inactive: bool = False,
    error_cls: type[TError] = OwnershipBoundaryNotFoundError,
    error_message: str = "Workspace not found",
) -> Workspace:
    filters = [
        Workspace.id == workspace_id,
        Workspace.user_id == user_id,
    ]
    if not include_inactive:
        filters.extend(
            [
                Workspace.archived_at.is_(None),
                Workspace.status.in_(["active", "paused"]),
            ]
        )
    workspace = db.scalar(select(Workspace).where(*filters))
    if workspace is None:
        raise error_cls(error_message)
    return workspace


def require_active_user_workspace_for_new_work(
    db: Session,
    *,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    not_found_error_cls: type[TError] = OwnershipBoundaryNotFoundError,
    inactive_error_cls: type[TError] = OwnershipBoundaryNotFoundError,
    not_found_message: str = "Workspace not found",
    inactive_message: str = "Workspace is not active",
) -> Workspace:
    workspace = require_user_workspace(
        db,
        user_id=user_id,
        workspace_id=workspace_id,
        include_inactive=True,
        error_cls=not_found_error_cls,
        error_message=not_found_message,
    )
    if not is_workspace_active_for_new_work(workspace):
        raise inactive_error_cls(inactive_message)
    return workspace


def require_user_role(
    db: Session,
    *,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    include_archived: bool = False,
    load_options: Sequence[ORMOption] = (),
    error_cls: type[TError] = OwnershipBoundaryNotFoundError,
    error_message: str = "Role not found",
) -> Role:
    filters = [
        Role.id == role_id,
        Role.user_id == user_id,
        Role.deleted_at.is_(None),
    ]
    if not include_archived:
        filters.append(Role.status != RoleStatus.ARCHIVED.value)
    statement = select(Role).where(*filters).options(*load_options)
    role = db.scalar(statement)
    if role is None:
        raise error_cls(error_message)
    return role


def require_user_application(
    db: Session,
    *,
    user_id: uuid.UUID,
    application_id: uuid.UUID,
    load_options: Sequence[ORMOption] = (),
    error_cls: type[TError] = OwnershipBoundaryNotFoundError,
    error_message: str = "Application workflow not found",
) -> Application:
    statement = (
        select(Application)
        .where(
            Application.id == application_id,
            Application.user_id == user_id,
            Application.deleted_at.is_(None),
        )
        .options(*load_options)
    )
    application = db.scalar(statement)
    if application is None:
        raise error_cls(error_message)
    return application
