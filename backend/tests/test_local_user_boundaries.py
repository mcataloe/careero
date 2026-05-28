from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.applications import (
    ApplicationMetadataUpdate,
    ApplicationNoteCreate,
    ApplicationNoteUpdate,
)
from app.schemas.roles import CompanyLookup, RoleCreate, RoleUpdate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate, WorkspaceUpdate
from app.seed import seed_default_job_sources, seed_local_data
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowService,
)
from app.services.current_user import CurrentUserContext
from app.services.roles import RoleNotFoundError, RoleService
from app.services.workspaces import (
    WorkspaceNotFoundError,
    WorkspaceService,
)


@pytest.fixture
def local_boundary_contexts(db_session: Session):
    user_a, _ = seed_local_data(db_session)
    user_b = User(
        id=uuid4(),
        email="other-local-user@careero.local",
        first_name="Other",
        last_name="Local User",
        display_name="Other Local User",
    )
    db_session.add(user_b)
    db_session.commit()
    seed_default_job_sources(db_session, user_b)

    context_a = CurrentUserContext(
        user_id=user_a.id,
        email=user_a.email,
        first_name=user_a.first_name,
        last_name=user_a.last_name,
        display_name=user_a.display_name,
        mode="test",
    )
    context_b = CurrentUserContext(
        user_id=user_b.id,
        email=user_b.email,
        first_name=user_b.first_name,
        last_name=user_b.last_name,
        display_name=user_b.display_name,
        mode="test",
    )

    workspace_a = WorkspaceService(
        db_session,
        current_user_context=context_a,
    ).create_workspace(WorkspaceCreate(title="User A workspace"))
    workspace_b = WorkspaceService(
        db_session,
        current_user_context=context_b,
    ).create_workspace(WorkspaceCreate(title="User B workspace"))

    return {
        "context_a": context_a,
        "context_b": context_b,
        "workspace_a": workspace_a,
        "workspace_b": workspace_b,
    }


def _create_role(
    db_session: Session,
    *,
    context: CurrentUserContext,
    workspace_id: UUID,
    title: str,
):
    return RoleService(db_session, current_user_context=context).create_role(
        RoleCreate(
            workspace_id=workspace_id,
            title=title,
            company=CompanyLookup(name=f"{title} Company"),
            source=SourceLookup(source_type="manual"),
            status="found",
        )
    )


def _as_uuid(value) -> UUID:
    return value if isinstance(value, UUID) else UUID(value)


def test_user_cannot_fetch_update_or_archive_another_users_workspace(
    db_session: Session,
    local_boundary_contexts,
) -> None:
    context_a = local_boundary_contexts["context_a"]
    context_b = local_boundary_contexts["context_b"]
    workspace_b = local_boundary_contexts["workspace_b"]
    user_a_workspaces = WorkspaceService(db_session, current_user_context=context_a)

    with pytest.raises(WorkspaceNotFoundError):
        user_a_workspaces.get_by_id(workspace_b.id, include_inactive=True)
    with pytest.raises(WorkspaceNotFoundError):
        user_a_workspaces.update_workspace(
            workspace_b.id,
            WorkspaceUpdate(title="Cross-user overwrite"),
        )
    with pytest.raises(WorkspaceNotFoundError):
        user_a_workspaces.archive_workspace(workspace_b.id)

    refreshed_b = WorkspaceService(
        db_session,
        current_user_context=context_b,
    ).get_by_id(workspace_b.id, include_inactive=True)
    assert refreshed_b.title == "User B workspace"
    assert refreshed_b.status == "active"


def test_user_cannot_fetch_update_or_archive_another_users_role(
    db_session: Session,
    local_boundary_contexts,
) -> None:
    context_a = local_boundary_contexts["context_a"]
    context_b = local_boundary_contexts["context_b"]
    workspace_b = local_boundary_contexts["workspace_b"]
    role_b = _create_role(
        db_session,
        context=context_b,
        workspace_id=workspace_b.id,
        title="User B opportunity",
    )
    user_a_roles = RoleService(db_session, current_user_context=context_a)

    with pytest.raises(RoleNotFoundError):
        user_a_roles.get_role(role_b.id)
    with pytest.raises(RoleNotFoundError):
        user_a_roles.update_role(role_b.id, RoleUpdate(title="Nope"))
    with pytest.raises(RoleNotFoundError):
        user_a_roles.archive_role(role_b.id)

    refreshed_b = RoleService(
        db_session,
        current_user_context=context_b,
    ).get_role(role_b.id)
    assert refreshed_b.title == "User B opportunity"
    assert refreshed_b.deleted_at is None


def test_user_cannot_fetch_or_update_another_users_application(
    db_session: Session,
    local_boundary_contexts,
) -> None:
    context_a = local_boundary_contexts["context_a"]
    context_b = local_boundary_contexts["context_b"]
    workspace_b = local_boundary_contexts["workspace_b"]
    role_b = _create_role(
        db_session,
        context=context_b,
        workspace_id=workspace_b.id,
        title="User B application role",
    )
    app_b = ApplicationWorkflowService(
        db_session,
        current_user_context=context_b,
    ).get_or_create_for_role(role_b.id)
    user_a_applications = ApplicationWorkflowService(
        db_session,
        current_user_context=context_a,
    )

    with pytest.raises(ApplicationWorkflowNotFoundError):
        user_a_applications.get_application(_as_uuid(app_b["id"]))
    with pytest.raises(ApplicationWorkflowNotFoundError):
        user_a_applications.get_application_for_role(role_b.id)
    with pytest.raises(ApplicationWorkflowNotFoundError):
        user_a_applications.get_timeline_for_role(role_b.id)
    with pytest.raises(ApplicationWorkflowNotFoundError):
        user_a_applications.update_application(
            _as_uuid(app_b["id"]),
            ApplicationMetadataUpdate(workflow_metadata={"priority": "stolen"}),
        )

    refreshed_b = ApplicationWorkflowService(
        db_session,
        current_user_context=context_b,
    ).get_application(_as_uuid(app_b["id"]))
    assert refreshed_b["workflow_metadata"]["createdFromRole"] is True
    assert "priority" not in refreshed_b["workflow_metadata"]


def test_application_child_records_remain_scoped_through_parent_application(
    db_session: Session,
    local_boundary_contexts,
) -> None:
    context_a = local_boundary_contexts["context_a"]
    context_b = local_boundary_contexts["context_b"]
    workspace_a = local_boundary_contexts["workspace_a"]
    workspace_b = local_boundary_contexts["workspace_b"]
    role_a = _create_role(
        db_session,
        context=context_a,
        workspace_id=workspace_a.id,
        title="User A application role",
    )
    role_b = _create_role(
        db_session,
        context=context_b,
        workspace_id=workspace_b.id,
        title="User B child role",
    )
    service_a = ApplicationWorkflowService(db_session, current_user_context=context_a)
    service_b = ApplicationWorkflowService(db_session, current_user_context=context_b)
    app_a = service_a.get_or_create_for_role(role_a.id)
    app_b = service_b.get_or_create_for_role(role_b.id)
    note_b = service_b.create_note(
        _as_uuid(app_b["id"]),
        ApplicationNoteCreate(body="User B private note."),
    )

    with pytest.raises(ApplicationWorkflowNotFoundError):
        service_a.list_notes(_as_uuid(app_b["id"]))
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service_a.update_note(
            _as_uuid(app_a["id"]),
            note_b["id"],
            ApplicationNoteUpdate(body="Cross-user child overwrite"),
        )

    assert (
        service_b.list_notes(_as_uuid(app_b["id"]))[0]["body"]
        == "User B private note."
    )
