from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.constants import ApplicationWorkflowState, StrideEvaluationStatus, WorkspaceType
from app.database import get_db
from app.main import create_app
from app.models import Application, AutomationSuggestion, StrideEvaluation
from app.schemas.applications import (
    ApplicationInterviewStageCreate,
    ApplicationStateTransitionRequest,
)
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate, WorkspaceMoney, WorkspacePreferences
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.roles import RoleService
from app.services.strategy import CareerStrategyService
from app.services.workspaces import WorkspaceService


def _create_role(
    db_session: Session,
    *,
    title: str,
    company: str,
    workspace_id=None,
    compensation_min: Decimal | None = None,
    compensation_max: Decimal | None = None,
    raw_description: str = "Build Python platform services with reliable delivery.",
):
    return RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=workspace_id,
            title=title,
            company=CompanyLookup(name=company),
            source=SourceLookup(source_type="manual"),
            raw_description=raw_description,
            compensation_min=compensation_min,
            compensation_max=compensation_max,
            compensation_currency="USD" if compensation_min is not None else None,
            parse_metadata={"roleCategory": "platform"},
        )
    )


def _create_application(db_session: Session, role_id) -> Application:
    detail = ApplicationWorkflowService(db_session).get_or_create_for_role(role_id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    return application


def _add_stride(
    db_session: Session,
    application: Application,
    *,
    score: Decimal,
    missing_keywords: list[str],
):
    db_session.add(
        StrideEvaluation(
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            role_id=application.role_id,
            evaluation_status=StrideEvaluationStatus.COMPLETED.value,
            overall_score=score,
            recommendation="apply" if score >= 75 else "monitor",
            confidence_level="medium",
            summary="Stored deterministic STRIDE evidence.",
            strengths=[
                {"label": "Platform leadership", "message": "Platform work is explicit."}
            ],
            concerns=[
                {"message": "Kubernetes evidence is thin."}
                if "kubernetes" in missing_keywords
                else {"message": "Scope needs review."}
            ],
            compensation_alignment={"status": "aligned" if score >= 75 else "below_target"},
            missing_keywords=missing_keywords,
        )
    )


def test_strategy_service_returns_insufficient_data_without_mutation(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    before = db_session.scalar(select(func.count(AutomationSuggestion.id)))

    summary = CareerStrategyService(db_session).get_workspace_strategy(
        workspace_id=DEFAULT_WORKSPACE_ID
    )

    after = db_session.scalar(select(func.count(AutomationSuggestion.id)))
    assert after == before
    assert summary.workspace_id == DEFAULT_WORKSPACE_ID
    assert summary.confidence.confidence == "insufficient_data"
    assert {item.reason for item in summary.insufficient_data} >= {
        "empty_workspace",
        "few_applications",
        "missing_stride_evaluations",
    }
    assert "stored Careero data" in summary.summary
    assert summary.action_candidates == []


def test_strategy_service_synthesizes_workspace_signals(db_session: Session) -> None:
    seed_local_data(db_session)
    workflow = ApplicationWorkflowService(db_session)
    first_role = _create_role(
        db_session,
        title="Staff Platform Engineer",
        company="Fit Co",
        compensation_min=Decimal("180000"),
        compensation_max=Decimal("210000"),
    )
    second_role = _create_role(
        db_session,
        title="Senior Platform Engineer",
        company="Quiet Co",
        compensation_min=Decimal("120000"),
        compensation_max=Decimal("135000"),
    )
    third_role = _create_role(
        db_session,
        title="Senior Infrastructure Engineer",
        company="Gap Co",
        compensation_min=Decimal("125000"),
        compensation_max=Decimal("140000"),
    )
    first = _create_application(db_session, first_role.id)
    second = _create_application(db_session, second_role.id)
    third = _create_application(db_session, third_role.id)
    for application in (first, second, third):
        workflow.transition_state(
            application.id,
            ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
        )
        workflow.transition_state(
            application.id,
            ApplicationStateTransitionRequest(state=ApplicationWorkflowState.APPLIED),
        )
        application.applied_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    workflow.create_interview_stage(
        first.id,
        ApplicationInterviewStageCreate(
            stage_type="recruiter_screen",
            title="Recruiter screen",
        ),
    )
    _add_stride(db_session, first, score=Decimal("86"), missing_keywords=["kubernetes"])
    _add_stride(db_session, second, score=Decimal("58"), missing_keywords=["kubernetes"])
    _add_stride(db_session, third, score=Decimal("62"), missing_keywords=["kubernetes"])
    db_session.commit()

    summary = CareerStrategyService(db_session).get_workspace_strategy(
        workspace_id=DEFAULT_WORKSPACE_ID
    )

    assert summary.sample_size.opportunities == 3
    assert summary.sample_size.submitted_applications == 3
    assert summary.sample_size.responses == 1
    assert summary.compensation_alignment.summary
    assert any(theme.label == "kubernetes" for theme in summary.skill_gap_themes)
    assert summary.role_market_positioning.themes
    assert summary.action_candidates
    assert all(candidate.advisory_only for candidate in summary.action_candidates)
    assert any("not external market data" in warning for warning in summary.warnings)


def test_strategy_api_returns_camel_case_contract_shape(
    application_client: TestClient,
) -> None:
    response = application_client.get(f"/api/strategy/workspaces/{DEFAULT_WORKSPACE_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["contractVersion"] == "careero.contracts.v1"
    assert body["workspaceId"] == str(DEFAULT_WORKSPACE_ID)
    assert "sampleSize" in body
    assert "sourceInputs" in body
    assert "actionCandidates" in body


def test_cross_workspace_strategy_comparison(db_session: Session) -> None:
    seed_local_data(db_session)
    second_workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(
            title="Contract search",
            workspace_type=WorkspaceType.CONTRACT_CONSULTING,
            preferences=WorkspacePreferences(
                targetCompensation=WorkspaceMoney(
                    min=125,
                    currency="USD",
                    period="hourly",
                    sourceText="$125/hr",
                )
            ),
        )
    )
    _create_role(
        db_session,
        title="Fractional Platform Consultant",
        company="Consult Co",
        workspace_id=second_workspace.id,
        compensation_min=Decimal("90"),
        compensation_max=Decimal("100"),
    )
    db_session.commit()

    strategy = CareerStrategyService(db_session).get_career_strategy(
        include_cross_track=True
    )

    assert strategy.cross_track_comparison is not None
    assert len(strategy.tracks) == 2
    assert len(strategy.cross_track_comparison.tracks) == 2
    assert "internal comparison" in strategy.cross_track_comparison.warnings[0]

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
