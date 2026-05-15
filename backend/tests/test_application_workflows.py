from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import (
    ActivityLog,
    Application,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    ApplicationStateHistory,
)
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate
from app.schemas.applications import ApplicationStateTransitionRequest
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.roles import RoleService
from app.services.workspaces import WorkspaceService


@pytest.fixture
def application_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_role(db_session: Session, *, status: str = "found", workspace_id=None):
    return RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=workspace_id,
            title="Senior Platform Engineer",
            company=CompanyLookup(name="Workflow Co"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/platform",
            raw_description="Build Python platforms.",
            status=status,
        )
    )


def test_service_creates_canonical_application_workflow(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session, status="interested")

    contract = ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)

    assert contract["contractVersion"] == "careero.contracts.v1"
    assert contract["workspaceId"] == str(DEFAULT_WORKSPACE_ID)
    assert contract["opportunityId"] == str(role.id)
    assert contract["currentState"] == "interested"
    assert contract["stateHistory"][0]["state"] == "interested"
    assert contract["reminders"] == []
    assert contract["notes"] == []
    assert contract["interviewStages"] == []

    application = db_session.scalar(select(Application).where(Application.role_id == role.id))
    assert application is not None
    assert application.workspace_id == DEFAULT_WORKSPACE_ID
    assert application.current_state == "interested"
    assert application.status == "interested"


def test_api_state_transition_and_typed_workflow_records(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)

    create_response = application_client.post(f"/api/roles/{role.id}/application")
    assert create_response.status_code == 201
    application = create_response.json()
    assert application["currentState"] == "discovered"
    application_id = application["id"]
    application_uuid = UUID(application_id)

    transition_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "interviewing", "reason": "Recruiter screen scheduled."},
    )
    assert transition_response.status_code == 200
    transitioned = transition_response.json()
    assert transitioned["currentState"] == "interviewing"
    assert [entry["state"] for entry in transitioned["stateHistory"]] == [
        "discovered",
        "interviewing",
    ]

    note_response = application_client.post(
        f"/api/applications/{application_id}/notes",
        json={"body": "Ask about platform ownership.", "author": "Local User"},
    )
    assert note_response.status_code == 200
    assert note_response.json()["notes"][0]["body"] == "Ask about platform ownership."

    reminder_response = application_client.post(
        f"/api/applications/{application_id}/reminders",
        json={
            "due_at": "2026-05-20T15:00:00Z",
            "title": "Follow up",
            "notes": "Send thank-you note.",
        },
    )
    assert reminder_response.status_code == 200
    reminder = reminder_response.json()["reminders"][0]
    assert reminder["completedAt"] is None
    assert reminder_response.json()["metadata"]["nextActionAt"] is not None

    complete_reminder_response = application_client.post(
        f"/api/applications/{application_id}/reminders/{reminder['id']}/complete"
    )
    assert complete_reminder_response.status_code == 200
    assert complete_reminder_response.json()["reminders"][0]["completedAt"] is not None
    assert complete_reminder_response.json()["metadata"]["nextActionAt"] is None

    interview_response = application_client.post(
        f"/api/applications/{application_id}/interview-stages",
        json={
            "stage_type": "recruiter_screen",
            "title": "Recruiter screen",
            "scheduled_at": "2026-05-22T16:00:00Z",
            "location": "Video",
            "notes": "Discuss scope.",
            "metadata": {"round": 1},
        },
    )
    assert interview_response.status_code == 200
    stage = interview_response.json()["interviewStages"][0]
    assert stage["stageType"] == "recruiter_screen"
    assert stage["metadata"]["round"] == 1

    link_response = application_client.post(
        f"/api/applications/{application_id}/external-links",
        json={
            "label": "Job posting",
            "url": "https://example.com/jobs/platform",
            "type": "posting",
        },
    )
    assert link_response.status_code == 200
    assert link_response.json()["externalLinks"][0]["type"] == "posting"

    assert db_session.scalar(
        select(ApplicationNote).where(ApplicationNote.application_id == application_uuid)
    ) is not None
    assert db_session.scalar(
        select(ApplicationReminder).where(ApplicationReminder.application_id == application_uuid)
    ) is not None
    assert db_session.scalar(
        select(ApplicationInterviewStage).where(
            ApplicationInterviewStage.application_id == application_uuid
        )
    ) is not None

    actions = list(
        db_session.scalars(
            select(ActivityLog.action)
            .where(ActivityLog.entity_id == application_uuid)
            .order_by(ActivityLog.created_at)
        )
    )
    assert "application.created" in actions
    assert "application.state_changed" in actions
    assert "application.note.created" in actions
    assert "application.reminder.created" in actions


def test_application_archive_and_active_listing(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application = application_client.post(f"/api/roles/{role.id}/application").json()
    application_id = application["id"]

    archive_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "archived", "reason": "No longer pursuing."},
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["currentState"] == "archived"
    assert archive_response.json()["metadata"]["archivedAt"] is not None

    active_list = application_client.get("/api/applications")
    assert active_list.status_code == 200
    assert application_id not in [item["id"] for item in active_list.json()]

    inactive_list = application_client.get(
        "/api/applications",
        params={"include_inactive": True},
    )
    assert inactive_list.status_code == 200
    assert application_id in [item["id"] for item in inactive_list.json()]

    reactivate_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "interested", "reason": "Reopened."},
    )
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["metadata"]["archivedAt"] is None
    assert reactivate_response.json()["metadata"]["reactivatedAt"] is not None


def test_archived_workspace_rejects_new_application_workflow(
    application_client: TestClient,
    db_session: Session,
) -> None:
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Archive Test Workspace")
    )
    role = create_role(db_session, workspace_id=workspace.id)
    WorkspaceService(db_session).archive_workspace(workspace.id)

    response = application_client.post(f"/api/roles/{role.id}/application")

    assert response.status_code == 409
    assert db_session.scalar(select(Application).where(Application.role_id == role.id)) is None


def test_application_state_history_persists_archive_fields(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    contract = service.get_or_create_for_role(role.id)

    archived = service.transition_state(
        UUID(contract["id"]),
        ApplicationStateTransitionRequest(state="archived", reason="Closed."),
    )

    assert archived["currentState"] == "archived"
    history = list(
        db_session.scalars(
            select(ApplicationStateHistory)
            .where(
                ApplicationStateHistory.application_id == UUID(contract["id"])
            )
            .order_by(ApplicationStateHistory.changed_at, ApplicationStateHistory.id)
        )
    )
    assert [entry.to_state for entry in history] == ["discovered", "archived"]
    persisted = db_session.get(Application, UUID(contract["id"]))
    assert persisted is not None
    assert persisted.archived_at is not None
