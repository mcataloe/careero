from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.main import create_app
from app.seed import seed_local_data


@pytest.fixture
def layer2_client(
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


def test_layer2_role_resume_evaluation_cache_force_and_activity_flow(
    layer2_client: TestClient,
) -> None:
    role_response = layer2_client.post(
        "/api/roles",
        json={
            "title": "Senior Platform Engineer",
            "company": {"name": "Layer Two Co", "website_url": "https://example.com"},
            "source": {"source_type": "manual"},
            "job_url": "https://example.com/jobs/platform",
            "location": "Chicago, IL",
            "remote_type": "hybrid",
            "compensation_min": "130000",
            "compensation_max": "160000",
            "compensation_currency": "USD",
            "raw_description": "Build Python and PostgreSQL platforms with FastAPI.",
            "status": "found",
            "date_found": "2026-05-13",
        },
    )
    assert role_response.status_code == 201
    role = role_response.json()

    source_response = layer2_client.post(
        "/api/resume-sources",
        json={
            "name": "Master Resume",
            "source_type": "master_resume",
            "version_label": "v1",
            "raw_text": "Built Python services and PostgreSQL-backed platforms.",
            "normalized_summary": "Backend platform engineer.",
            "is_active": True,
        },
    )
    assert source_response.status_code == 201

    evaluation_payload = {
        "user_context": {
            "preferred_remote_type": "hybrid",
            "target_keywords": ["python", "postgresql", "fastapi"],
        }
    }
    first_response = layer2_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json=evaluation_payload,
    )
    assert first_response.status_code == 201
    first = first_response.json()
    assert first["role_id"] == role["id"]
    assert first["evaluation_status"] == "completed"
    assert first["overall_score"] is not None
    assert first["source_hash"] is not None
    assert first["evaluation_input_hash"] is not None
    assert first["ai_status"] == "skipped"

    latest_response = layer2_client.get(f"/api/roles/{role['id']}/evaluations/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == first["id"]

    cached_response = layer2_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json=evaluation_payload,
    )
    assert cached_response.status_code == 200
    assert cached_response.json()["id"] == first["id"]

    forced_response = layer2_client.post(
        f"/api/roles/{role['id']}/evaluations",
        json={**evaluation_payload, "force": True},
    )
    assert forced_response.status_code == 201
    forced = forced_response.json()
    assert forced["id"] != first["id"]
    assert forced["evaluation_input_hash"] == first["evaluation_input_hash"]

    activity_response = layer2_client.get(
        "/api/activity-log",
        params={"entity_type": "stride_evaluation", "entity_id": first["id"]},
    )
    assert activity_response.status_code == 200
    first_actions = {entry["action"] for entry in activity_response.json()}
    assert {
        "stride_evaluation.started",
        "stride_evaluation.completed",
        "stride_evaluation.cached_result_reused",
    }.issubset(first_actions)

    completed_response = layer2_client.get(
        "/api/activity-log",
        params={"action": "stride_evaluation.completed", "limit": 10},
    )
    assert completed_response.status_code == 200
    assert len(completed_response.json()) >= 2
