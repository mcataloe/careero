from collections.abc import Generator
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import StrideEvaluationStatus
from app.database import get_db
from app.main import create_app
from app.models import (
    ActivityLog,
    Application,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    GeneratedArtifact,
    StrideEvaluation,
    User,
)
from app.schemas.applications import ApplicationMetadataUpdate
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate
from app.seed import DEFAULT_LOCAL_USER_ID, DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowSeedMissingError,
    ApplicationWorkflowService,
    ApplicationWorkflowWorkspaceInactiveError,
)
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


def create_role(
    db_session: Session,
    *,
    company_name: str = "Workflow Co",
    title: str = "Senior Platform Engineer",
    status: str = "found",
    workspace_id=None,
):
    return RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=workspace_id,
            title=title,
            company=CompanyLookup(name=company_name, website_url="https://example.com"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/platform",
            location="Chicago, IL",
            remote_type="hybrid",
            raw_description="Build Python platforms.",
            status=status,
        )
    )


def add_workflow_children(db_session: Session, application: Application) -> None:
    db_session.add_all(
        [
            ApplicationNote(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                author="Local User",
                body="Follow up on platform ownership.",
            ),
            ApplicationReminder(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                due_at=application.created_at,
                title="Follow up",
            ),
            ApplicationInterviewStage(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                stage_type="recruiter_screen",
                title="Recruiter screen",
            ),
        ]
    )
    db_session.commit()


def add_summary_sources(db_session: Session, application: Application) -> None:
    db_session.add(
        StrideEvaluation(
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            role_id=application.role_id,
            evaluation_status=StrideEvaluationStatus.COMPLETED.value,
            overall_score=Decimal("82.50"),
            recommendation="apply",
            confidence_level="high",
            summary="Strong platform fit.",
        )
    )
    db_session.add_all(
        [
            GeneratedArtifact(
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                artifact_type="tailored_resume",
                title="Tailored resume",
                content="resume",
                artifact_metadata={
                    "contract": {
                        "revision": {"revisionNumber": 2},
                    }
                },
            ),
            GeneratedArtifact(
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                artifact_type="cover_letter",
                title="Cover letter",
                content="letter",
                artifact_metadata={
                    "contract": {
                        "revision": {"revisionNumber": 1},
                    }
                },
            ),
        ]
    )
    db_session.commit()


def test_service_ensures_workflow_and_prevents_duplicate(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session, status="interested")
    service = ApplicationWorkflowService(db_session)

    first = service.get_or_create_for_role(role.id)
    second = service.get_or_create_for_role(role.id)

    assert first["id"] == second["id"]
    assert first["current_state"] == "interested"
    assert first["role"]["id"] == role.id
    applications = list(db_session.scalars(select(Application).where(Application.role_id == role.id)))
    assert len(applications) == 1
    assert applications[0].status == applications[0].current_state


def test_service_lists_by_workspace_and_aggregates_summaries(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    other_workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Contract Search")
    )
    default_role = create_role(db_session, company_name="Default Co")
    other_role = create_role(
        db_session,
        company_name="Other Co",
        workspace_id=other_workspace.id,
    )
    service = ApplicationWorkflowService(db_session)
    default_detail = service.get_or_create_for_role(default_role.id)
    service.get_or_create_for_role(other_role.id)
    default_application = db_session.get(Application, UUID(default_detail["id"]))
    assert default_application is not None
    add_workflow_children(db_session, default_application)
    add_summary_sources(db_session, default_application)

    all_items = service.list_applications()
    default_items = service.list_applications(workspace_id=DEFAULT_WORKSPACE_ID)
    other_items = service.list_applications(workspace_id=other_workspace.id)

    assert {item["workspace_id"] for item in all_items} == {
        DEFAULT_WORKSPACE_ID,
        other_workspace.id,
    }
    assert [item["role_id"] for item in default_items] == [default_role.id]
    assert [item["role_id"] for item in other_items] == [other_role.id]
    item = default_items[0]
    assert item["title"] == "Senior Platform Engineer"
    assert item["company"]["name"] == "Default Co"
    assert item["stride"]["summary"] == "Strong platform fit."
    assert item["resume_artifact"]["revision_number"] == 2
    assert item["cover_letter_artifact"]["revision_number"] == 1
    assert item["counts"] == {"notes": 1, "reminders": 1, "interviews": 1}


def test_service_detail_and_metadata_update(db_session: Session) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)

    updated = service.update_application(
        UUID(detail["id"]),
        ApplicationMetadataUpdate(
            workflow_metadata={"priority": "high"},
            applied_at="2026-05-16T15:00:00Z",
        ),
    )

    assert updated["workflow_metadata"]["createdFromRole"] is True
    assert updated["workflow_metadata"]["priority"] == "high"
    assert updated["current_state"] == "discovered"
    assert updated["application_state"]["currentState"] == "discovered"
    assert updated["state_history"][0]["state"] == "discovered"

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == UUID(detail["id"]))
        )
    )
    assert "application.updated" in actions


def test_api_list_detail_ensure_filter_and_update(
    application_client: TestClient,
    db_session: Session,
) -> None:
    other_workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Leadership Search")
    )
    default_role = create_role(db_session, company_name="Default API Co")
    other_role = create_role(
        db_session,
        company_name="Other API Co",
        workspace_id=other_workspace.id,
    )

    default_response = application_client.post(f"/api/roles/{default_role.id}/application")
    duplicate_response = application_client.post(f"/api/roles/{default_role.id}/application")
    other_response = application_client.post(f"/api/roles/{other_role.id}/application")

    assert default_response.status_code == 201
    assert duplicate_response.status_code == 201
    assert default_response.json()["id"] == duplicate_response.json()["id"]
    assert other_response.status_code == 201

    list_response = application_client.get("/api/applications")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    filtered_response = application_client.get(
        "/api/applications",
        params={"workspace_id": str(DEFAULT_WORKSPACE_ID)},
    )
    assert filtered_response.status_code == 200
    assert [item["role_id"] for item in filtered_response.json()] == [
        str(default_role.id)
    ]

    workspace_response = application_client.get(
        f"/api/workspaces/{other_workspace.id}/applications"
    )
    assert workspace_response.status_code == 200
    assert [item["role_id"] for item in workspace_response.json()] == [
        str(other_role.id)
    ]

    application_id = default_response.json()["id"]
    detail_response = application_client.get(f"/api/applications/{application_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["role"]["company"]["name"] == "Default API Co"
    assert detail_response.json()["application_state"]["currentState"] == "discovered"

    update_response = application_client.patch(
        f"/api/applications/{application_id}",
        json={
            "workflow_metadata": {"priority": "medium"},
            "next_action_at": "2026-05-20T15:00:00Z",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["workflow_metadata"]["priority"] == "medium"
    assert update_response.json()["next_action_at"] is not None


def test_api_workspace_scope_and_inactive_filtering(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application = application_client.post(f"/api/roles/{role.id}/application").json()
    application_id = application["id"]

    archive_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "archived", "reason": "Closed."},
    )
    assert archive_response.status_code == 200

    active_response = application_client.get("/api/applications")
    assert active_response.status_code == 200
    assert active_response.json() == []

    inactive_response = application_client.get(
        "/api/applications",
        params={"include_inactive": True},
    )
    assert inactive_response.status_code == 200
    assert [item["id"] for item in inactive_response.json()] == [application_id]

    missing_workspace_response = application_client.get(
        "/api/applications",
        params={"workspace_id": str(uuid4())},
    )
    assert missing_workspace_response.status_code == 404


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


def test_service_not_found_and_seed_missing_errors(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.get_application(uuid4())

    user = db_session.get(User, DEFAULT_LOCAL_USER_ID)
    assert user is not None
    user.deleted_at = datetime.now(timezone.utc)
    db_session.commit()
    with pytest.raises(ApplicationWorkflowSeedMissingError):
        service.list_applications()


def test_service_rejects_inactive_workspace(db_session: Session) -> None:
    seed_local_data(db_session)
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Inactive Workspace")
    )
    role = create_role(db_session, workspace_id=workspace.id)
    WorkspaceService(db_session).archive_workspace(workspace.id)

    with pytest.raises(ApplicationWorkflowWorkspaceInactiveError):
        ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)
