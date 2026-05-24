from collections.abc import Generator
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ApplicationWorkflowState
from app.database import get_db
from app.main import create_app
from app.models import Application, AutomationApprovalLog, GeneratedArtifact
from app.schemas.applications import ApplicationStateTransitionRequest
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.roles import RoleService


@pytest.fixture
def automation_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_application(db_session: Session) -> Application:
    role = RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=DEFAULT_WORKSPACE_ID,
            title="Senior Platform Engineer",
            company=CompanyLookup(name="Automation Co", website_url="https://example.com"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/platform",
            location="Remote",
            remote_type="remote",
            raw_description="Build internal developer platforms.",
            status="found",
        )
    )
    service = ApplicationWorkflowService(db_session)
    application = service.get_or_create_for_role(role.id)
    application_id = application["id"]
    service.transition_state(
        application_id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
    )
    service.transition_state(
        application_id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.APPLIED),
    )
    stored = db_session.get(Application, application_id)
    assert stored is not None
    stored.applied_at = datetime.now(timezone.utc) - timedelta(days=10)
    db_session.commit()
    return stored


def test_generates_workspace_scoped_follow_up_and_draft_suggestions(
    db_session: Session,
    automation_client: TestClient,
) -> None:
    application = create_application(db_session)

    response = automation_client.get(
        f"/api/automation/suggestions?workspace_id={application.workspace_id}"
    )

    assert response.status_code == 200
    body = response.json()
    actions = {item["action_type"] for item in body["suggestions"]}
    assert "follow_up_suggestion" in actions
    assert "communication_draft" in actions
    assert body["external_actions_enabled"] is False
    assert all(
        item["workspace_id"] == str(application.workspace_id)
        for item in body["suggestions"]
    )
    assert all(
        item["preview"]["external_mutation"] is False
        for item in body["suggestions"]
    )


def test_approval_logs_decision_without_mutating_application_state(
    db_session: Session,
    automation_client: TestClient,
) -> None:
    application = create_application(db_session)
    suggestions = automation_client.get(
        f"/api/automation/suggestions?target_type=application&target_id={application.id}"
    ).json()["suggestions"]
    suggestion = next(item for item in suggestions if item["action_type"] == "follow_up_suggestion")

    response = automation_client.post(f"/api/automation/suggestions/{suggestion['id']}/approve")

    assert response.status_code == 200
    approval = response.json()
    assert approval["approval_status"] == "approved"
    assert approval["execution_status"] == "not_applicable"
    assert approval["external_mutation"] is False
    db_session.refresh(application)
    assert application.current_state == ApplicationWorkflowState.APPLIED.value
    assert db_session.scalar(select(AutomationApprovalLog)) is not None


def test_rejecting_suggestion_does_not_mutate_targets(
    db_session: Session,
    automation_client: TestClient,
) -> None:
    application = create_application(db_session)
    suggestions = automation_client.get(
        f"/api/automation/suggestions?target_type=application&target_id={application.id}"
    ).json()["suggestions"]
    suggestion = next(item for item in suggestions if item["action_type"] == "communication_draft")

    response = automation_client.post(
        f"/api/automation/suggestions/{suggestion['id']}/reject",
        json={"reason": "Not needed"},
    )

    assert response.status_code == 200
    assert response.json()["approval_status"] == "rejected"
    db_session.refresh(application)
    assert application.current_state == ApplicationWorkflowState.APPLIED.value


def test_artifact_readiness_suggestion_does_not_mark_artifact_submitted(
    db_session: Session,
    automation_client: TestClient,
) -> None:
    application = create_application(db_session)
    artifact = GeneratedArtifact(
        user_id=application.user_id,
        workspace_id=application.workspace_id,
        application_id=application.id,
        role_id=application.role_id,
        artifact_type="cover_letter",
        title="Automation Co cover letter",
        content="Draft cover letter.",
        artifact_metadata={
            "contract": {
                "lifecycleStatus": "draft",
                "generationMetadata": {"warnings": ["Review unsupported claim."]},
                "exportMetadata": [],
            }
        },
    )
    db_session.add(artifact)
    db_session.commit()

    response = automation_client.get(
        f"/api/automation/suggestions?target_type=artifact&target_id={artifact.id}"
    )

    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert any(item["action_type"] == "artifact_readiness_check" for item in suggestions)
    db_session.refresh(artifact)
    assert artifact.artifact_metadata["contract"]["lifecycleStatus"] == "draft"
    assert "submittedAt" not in artifact.artifact_metadata["contract"]


def test_preferences_keep_future_external_actions_disabled(
    automation_client: TestClient,
) -> None:
    response = automation_client.patch(
        f"/api/workspaces/{DEFAULT_WORKSPACE_ID}/automation-preferences",
        json={"future_external_actions_enabled": True},
    )

    assert response.status_code == 422
    preferences = automation_client.get(
        f"/api/workspaces/{DEFAULT_WORKSPACE_ID}/automation-preferences"
    ).json()
    assert preferences["future_external_actions_enabled"] is False
