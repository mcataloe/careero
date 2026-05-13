from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, Company, Role, User
from app.seed import DEFAULT_LOCAL_USER_ID, seed_local_data


@pytest.fixture
def stride_api_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def role_payload(company_name: str = "Stride Example") -> dict:
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
            "user_notes": "Evaluate this later with the real STRIDE engine.",
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
    role = Role(
        user_id=user.id,
        company_id=company.id,
        title="Wrong Scope Role",
        status="found",
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def test_create_evaluation_for_active_role_logs_activity(
    stride_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(stride_api_client)
    evaluation = create_evaluation(stride_api_client, role["id"])

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
    assert "AI evaluations are disabled" in (
        evaluation["raw_evaluation_json"]["ai_failure_reason"]
    )

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(
                ActivityLog.entity_id == UUID(evaluation["id"]),
                ActivityLog.entity_type == "stride_evaluation",
            )
        )
    )
    assert actions == ["stride_evaluation.created"]


def test_latest_list_and_get_evaluations(stride_api_client: TestClient) -> None:
    role = create_role(stride_api_client)
    evaluation = create_evaluation(stride_api_client, role["id"])

    latest_response = stride_api_client.get(
        f"/api/roles/{role['id']}/evaluations/latest"
    )
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == evaluation["id"]

    list_response = stride_api_client.get("/api/stride-evaluations")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [evaluation["id"]]

    filtered_response = stride_api_client.get(
        "/api/stride-evaluations",
        params={"role_id": role["id"], "evaluation_status": "completed"},
    )
    assert filtered_response.status_code == 200
    assert [item["id"] for item in filtered_response.json()] == [evaluation["id"]]

    detail_response = stride_api_client.get(
        f"/api/stride-evaluations/{evaluation['id']}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == evaluation["id"]


def test_create_evaluation_rejects_archived_missing_or_wrong_scope_roles(
    stride_api_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(stride_api_client)

    archive_response = stride_api_client.delete(f"/api/roles/{role['id']}")
    assert archive_response.status_code == 204

    archived_response = stride_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={},
    )
    assert archived_response.status_code == 404

    missing_response = stride_api_client.post(
        f"/api/roles/{uuid4()}/evaluations",
        json={},
    )
    assert missing_response.status_code == 404

    other_role = add_other_user_role(db_session)
    wrong_scope_response = stride_api_client.post(
        f"/api/roles/{other_role.id}/evaluations",
        json={},
    )
    assert wrong_scope_response.status_code == 404


def test_evaluation_validation_errors(stride_api_client: TestClient) -> None:
    role = create_role(stride_api_client)

    invalid_body_response = stride_api_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={"user_context": "not-an-object"},
    )
    assert invalid_body_response.status_code == 422

    invalid_query_response = stride_api_client.get(
        "/api/stride-evaluations",
        params={"evaluation_status": "unknown"},
    )
    assert invalid_query_response.status_code == 422


def test_latest_evaluation_returns_404_when_none_exist(
    stride_api_client: TestClient,
) -> None:
    role = create_role(stride_api_client)

    response = stride_api_client.get(f"/api/roles/{role['id']}/evaluations/latest")

    assert response.status_code == 404
