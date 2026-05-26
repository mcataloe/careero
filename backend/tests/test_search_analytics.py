from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.constants import ApplicationWorkflowState, CompassEvaluationStatus
from app.database import get_db
from app.main import create_app
from app.models import Application, ApplicationReminder, CompassEvaluation
from app.schemas.applications import (
    ApplicationInterviewStageCreate,
    ApplicationNoteCreate,
    ApplicationStateTransitionRequest,
)
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.seed import seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.roles import RoleService
from app.services.search_analytics import (
    SearchAnalyticsService,
    SearchAnalyticsWorkspaceNotFoundError,
)


def _create_role(
    db_session: Session,
    *,
    title: str,
    company: str,
    compensation_min: Decimal | None = None,
    compensation_max: Decimal | None = None,
):
    return RoleService(db_session).create_role(
        RoleCreate(
            title=title,
            company=CompanyLookup(name=company),
            source=SourceLookup(source_type="manual"),
            raw_description="Build reliable infrastructure platforms.",
            compensation_min=compensation_min,
            compensation_max=compensation_max,
        )
    )


def _create_application(db_session: Session, title: str, company: str) -> Application:
    role = _create_role(db_session, title=title, company=company)
    detail = ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    return application


def test_search_analytics_calculates_counts_conversions_and_segments(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    first = _create_application(db_session, "Senior Platform Engineer", "Fit Co")
    second = _create_application(db_session, "Staff Infrastructure Engineer", "Risk Co")
    third = _create_application(db_session, "Engineering Manager", "Quiet Co")

    service.transition_state(
        first.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
    )
    service.transition_state(
        first.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.APPLIED),
    )
    first.applied_at = datetime.now(timezone.utc) - timedelta(days=3)
    service.create_interview_stage(
        first.id,
        ApplicationInterviewStageCreate(
            stage_type="recruiter_screen",
            title="Recruiter screen",
        ),
    )
    service.create_note(
        first.id,
        ApplicationNoteCreate(body="Recruiter screen scheduled.", note_type="recruiter"),
    )
    reminder = ApplicationReminder(
        application_id=first.id,
        user_id=first.user_id,
        workspace_id=first.workspace_id,
        due_at=datetime.now(timezone.utc) - timedelta(days=1),
        title="Follow up",
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(reminder)
    service.transition_state(
        second.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
    )
    service.transition_state(
        second.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.APPLIED),
    )
    service.transition_state(
        third.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.ARCHIVED),
    )
    db_session.add_all(
        [
            CompassEvaluation(
                user_id=first.user_id,
                workspace_id=first.workspace_id,
                role_id=first.role_id,
                evaluation_status=CompassEvaluationStatus.COMPLETED.value,
                overall_score=Decimal("86"),
                compensation_alignment={"status": "aligned"},
            ),
            CompassEvaluation(
                user_id=second.user_id,
                workspace_id=second.workspace_id,
                role_id=second.role_id,
                evaluation_status=CompassEvaluationStatus.COMPLETED.value,
                overall_score=Decimal("52"),
                compensation_alignment={"status": "below_target"},
            ),
        ]
    )
    db_session.commit()

    analytics = SearchAnalyticsService(db_session).get_search_analytics()

    assert analytics["summary"]["opportunities_saved"]["value"] == 3
    assert analytics["summary"]["opportunities_archived"]["value"] == 1
    assert analytics["summary"]["applications_submitted"]["value"] == 2
    assert analytics["summary"]["interviews_received"]["value"] == 1
    assert analytics["summary"]["recruiter_contacts"]["value"] == 1
    assert analytics["summary"]["followups_completed"]["value"] == 1
    applied_to_interview = next(
        item
        for item in analytics["conversion_rates"]
        if item["from_stage"] == "applied" and item["to_stage"] == "interviewing"
    )
    assert applied_to_interview["numerator"] == 1
    assert applied_to_interview["denominator"] == 2
    assert applied_to_interview["rate"] == 0.5
    compass_segments = {
        item["segment"]: item for item in analytics["segment_response_rates"]
    }
    assert compass_segments["high_compass_fit"]["response_rate"] == 1
    assert compass_segments["low_compass_fit"]["response_rate"] == 0
    assert compass_segments["compensation_aligned"]["response_rate"] == 1
    assert compass_segments["compensation_risk"]["response_rate"] == 0


def test_search_analytics_rejects_unknown_workspace(db_session: Session) -> None:
    seed_local_data(db_session)

    with pytest.raises(SearchAnalyticsWorkspaceNotFoundError):
        SearchAnalyticsService(db_session).get_search_analytics(workspace_id=uuid4())


def test_search_analytics_api(application_client: TestClient) -> None:
    response = application_client.get("/api/analytics/search")

    assert response.status_code == 200
    assert response.json()["scope"] == "all_workspaces"


@pytest.fixture
def application_client(db_session: Session):
    seed_local_data(db_session)
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
