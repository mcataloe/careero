from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, Company, Role, CompassEvaluation, User, Workspace
from app.seed import DEFAULT_LOCAL_USER_ID, seed_local_data
from app.schemas.compass_evaluations import CompassEvaluationCreate
from app.services.compass_evaluations import CompassEvaluationService


@pytest.fixture
def compass_api_client(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("CAREERO_ENABLE_AI_EVALUATIONS", "false")
    monkeypatch.setenv("CAREERO_OPENAI_API_KEY", "")
    get_settings.cache_clear()
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def role_payload(company_name: str = "Compass Example") -> dict:
    return {
        "title": "Platform Engineer",
        "company": {
            "name": company_name,
            "website_url": "https://example.com",
        },
        "source": {
            "source_type": "manual",
        },
        "job_url": "https://example.com/jobs/platform-engineer",
        "location": "Chicago, IL",
        "remote_type": "hybrid",
        "raw_description": "Build internal platforms with Python and PostgreSQL.",
        "status": "found",
        "date_found": "2026-05-13",
    }


def create_role(client: TestClient) -> dict:
    response = client.post("/api/roles", json=role_payload())
    assert response.status_code == 201
    return response.json()


def create_evaluation(client: TestClient, role_id: str) -> dict:
    response = client.post(
        f"/api/roles/{role_id}/evaluations",
        json={
            "user_notes": "Evaluate this later with the real COMPASS engine.",
            "user_context": {
                "preferred_remote_type": "hybrid",
                "target_compensation_min": "110000",
                "target_seniority": "mid",
                "target_keywords": ["python", "postgresql"],
            },
        },
    )
    assert response.status_code == 201
    return response.json()


def add_other_user_role(db_session: Session) -> Role:
    user = User(
        email="other-user@careero.local",
        display_name="Other User",
    )
    db_session.add(user)
    db_session.flush()
    company = Company(user_id=user.id, name="Other Company")
    db_session.add(company)
    db_session.flush()
    workspace = Workspace(
        user_id=user.id,
        title="Other Workspace",
        workspace_type="full_time_individual_contributor",
        status="active",
        preferences={},
        tags=[],
        workspace_metadata={},
    )
    db_session.add(workspace)
    db_session.flush()
    role = Role(
        user_id=user.id,
        workspace_id=workspace.id,
        company_id=company.id,
        title="Wrong Scope Role",
        status="found",
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def test_create_evaluation_for_active_role_logs_activity(
    compass_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(compass_api_client)
    evaluation = create_evaluation(compass_api_client, role["id"])

    assert evaluation["role_id"] == role["id"]
    assert evaluation["user_id"] == str(DEFAULT_LOCAL_USER_ID)
    assert evaluation["evaluation_status"] == "completed"
    assert evaluation["overall_score"] is not None
    assert evaluation["recommendation"] in {
        "apply",
        "monitor",
        "skip",
        "needs_review",
    }
    assert evaluation["confidence_level"] in {"low", "medium", "high"}
    assert evaluation["resume_alignment"]["status"] == "baseline"
    assert evaluation["ats_keywords"] == ["postgresql", "python"]
    assert evaluation["missing_keywords"] == []
    assert (
        evaluation["raw_evaluation_json"]["ruleset_version"]
        == "phase_2b_deterministic_v1"
    )
    assert "dimension_scores" in evaluation["raw_evaluation_json"]
    assert evaluation["raw_evaluation_json"]["ai_status"] == "skipped"
    assert evaluation["model_used"] is None
    assert evaluation["prompt_version"] == "phase_2c_grounded_prompt_v1"
    assert evaluation["ruleset_version"] == "phase_2b_deterministic_v1"
    assert evaluation["latency_ms"] is not None
    assert evaluation["ai_enabled"] is False
    assert evaluation["ai_status"] == "skipped"
    assert evaluation["error_message"] is None
    assert evaluation["role_content_hash"]
    assert evaluation["evaluation_input_hash"]
    assert "AI evaluations are disabled" in (
        evaluation["raw_evaluation_json"]["ai_failure_reason"]
    )

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(
                ActivityLog.entity_id == UUID(evaluation["id"]),
                ActivityLog.entity_type == "compass_evaluation",
            )
        )
    )
    assert actions == [
        "compass_evaluation.started",
        "compass_evaluation.completed",
    ]


def test_create_evaluation_reuses_cache_for_same_inputs(
    compass_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(compass_api_client)
    first = create_evaluation(compass_api_client, role["id"])

    second_response = compass_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={
            "user_notes": "Evaluate this later with the real COMPASS engine.",
            "user_context": {
                "preferred_remote_type": "hybrid",
                "target_compensation_min": "110000",
                "target_seniority": "mid",
                "target_keywords": ["python", "postgresql"],
            },
        },
    )

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["id"] == first["id"]
    assert second["evaluation_input_hash"] == first["evaluation_input_hash"]
    assert db_session.query(CompassEvaluation).count() == 1

    actions = list(
        db_session.scalars(
            select(ActivityLog.action)
            .where(
                ActivityLog.entity_id == UUID(first["id"]),
                ActivityLog.entity_type == "compass_evaluation",
            )
            .order_by(ActivityLog.created_at, ActivityLog.action)
        )
    )
    assert "compass_evaluation.cached_result_reused" in actions


def test_force_rerun_creates_new_evaluation(compass_api_client: TestClient) -> None:
    role = create_role(compass_api_client)
    first = create_evaluation(compass_api_client, role["id"])

    second_response = compass_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={
            "force": True,
            "user_notes": "Evaluate this later with the real COMPASS engine.",
            "user_context": {
                "preferred_remote_type": "hybrid",
                "target_compensation_min": "110000",
                "target_seniority": "mid",
                "target_keywords": ["python", "postgresql"],
            },
        },
    )

    assert second_response.status_code == 201
    second = second_response.json()
    assert second["id"] != first["id"]
    assert second["evaluation_input_hash"] == first["evaluation_input_hash"]


def test_role_content_change_bypasses_cache(compass_api_client: TestClient) -> None:
    role = create_role(compass_api_client)
    first = create_evaluation(compass_api_client, role["id"])

    update_response = compass_api_client.patch(
        f"/api/roles/{role['id']}",
        json={"normalized_description": "Updated role text with Python and FastAPI."},
    )
    assert update_response.status_code == 200
    second = create_evaluation(compass_api_client, role["id"])

    assert second["id"] != first["id"]
    assert second["role_content_hash"] != first["role_content_hash"]
    assert second["evaluation_input_hash"] != first["evaluation_input_hash"]


def test_active_resume_source_change_bypasses_cache(
    compass_api_client: TestClient,
) -> None:
    role = create_role(compass_api_client)
    source_response = compass_api_client.post(
        "/api/resume-sources",
        json={
            "name": "Master Resume",
            "source_type": "master_resume",
            "version_label": "v1",
            "raw_text": "Python and PostgreSQL platform experience.",
            "normalized_summary": "Backend platform engineer.",
            "is_active": True,
        },
    )
    assert source_response.status_code == 201
    source = source_response.json()
    first = create_evaluation(compass_api_client, role["id"])

    version_response = compass_api_client.post(
        f"/api/resume-sources/{source['id']}/versions",
        json={
            "version_label": "v2",
            "raw_text": "Python, PostgreSQL, and FastAPI platform experience.",
            "normalized_summary": "Backend platform engineer with FastAPI.",
            "is_active": True,
        },
    )
    assert version_response.status_code == 201
    second = create_evaluation(compass_api_client, role["id"])

    assert second["id"] != first["id"]
    assert second["source_hash"] != first["source_hash"]
    assert second["evaluation_input_hash"] != first["evaluation_input_hash"]


class FailedEvaluator:
    def enrich(self, **kwargs) -> dict:
        return {
            "ai_status": "failed",
            "ai_enabled": True,
            "ai_model": "gpt-5-mini",
            "ai_latency_ms": 1,
            "ai_input_token_estimate": 42,
            "ai_output_token_estimate": None,
            "ai_error_type": "TimeoutError",
            "ai_failure_reason": "timeout for sk-REDACTED",
        }


def test_failed_ai_metadata_is_persisted_and_logged(
    compass_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(compass_api_client)
    service = CompassEvaluationService(
        db_session,
        settings=Settings(
            _env_file=None,
            enable_ai_evaluations=True,
            openai_api_key="sk-test",
        ),
        ai_evaluator=FailedEvaluator(),
    )

    result = service.create_for_role(
        role_id=UUID(role["id"]),
        payload=CompassEvaluationCreate(),
    )
    evaluation = result.evaluation

    assert result.reused_cache is False
    assert evaluation.ai_status == "failed"
    assert evaluation.model_used == "gpt-5-mini"
    assert evaluation.error_message == "timeout for sk-REDACTED"
    assert "sk-test" not in evaluation.error_message
    actions = list(
        db_session.scalars(
            select(ActivityLog.action)
            .where(ActivityLog.entity_id == evaluation.id)
            .order_by(ActivityLog.created_at, ActivityLog.action)
        )
    )
    assert "compass_evaluation.failed" in actions
    assert "compass_evaluation.completed" in actions


def test_latest_list_and_get_evaluations(compass_api_client: TestClient) -> None:
    role = create_role(compass_api_client)
    evaluation = create_evaluation(compass_api_client, role["id"])

    latest_response = compass_api_client.get(
        f"/api/roles/{role['id']}/evaluations/latest"
    )
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == evaluation["id"]

    list_response = compass_api_client.get("/api/compass-evaluations")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [evaluation["id"]]

    filtered_response = compass_api_client.get(
        "/api/compass-evaluations",
        params={"role_id": role["id"], "evaluation_status": "completed"},
    )
    assert filtered_response.status_code == 200
    assert [item["id"] for item in filtered_response.json()] == [evaluation["id"]]

    detail_response = compass_api_client.get(
        f"/api/compass-evaluations/{evaluation['id']}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == evaluation["id"]


def test_create_evaluation_rejects_archived_missing_or_wrong_scope_roles(
    compass_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(compass_api_client)

    archive_response = compass_api_client.delete(f"/api/roles/{role['id']}")
    assert archive_response.status_code == 204

    archived_response = compass_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={},
    )
    assert archived_response.status_code == 404

    missing_response = compass_api_client.post(
        f"/api/roles/{uuid4()}/evaluations",
        json={},
    )
    assert missing_response.status_code == 404

    other_role = add_other_user_role(db_session)
    wrong_scope_response = compass_api_client.post(
        f"/api/roles/{other_role.id}/evaluations",
        json={},
    )
    assert wrong_scope_response.status_code == 404


def test_evaluation_validation_errors(compass_api_client: TestClient) -> None:
    role = create_role(compass_api_client)

    invalid_body_response = compass_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={"user_context": "not-an-object"},
    )
    assert invalid_body_response.status_code == 422

    invalid_query_response = compass_api_client.get(
        "/api/compass-evaluations",
        params={"evaluation_status": "unknown"},
    )
    assert invalid_query_response.status_code == 422


def test_latest_evaluation_returns_404_when_none_exist(
    compass_api_client: TestClient,
) -> None:
    role = create_role(compass_api_client)

    response = compass_api_client.get(f"/api/roles/{role['id']}/evaluations/latest")

    assert response.status_code == 404
