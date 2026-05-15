from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.main import create_app
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data


@pytest.fixture
def workspace_client(
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


def test_workspace_crud_archive_and_reactivate(workspace_client: TestClient) -> None:
    create_response = workspace_client.post(
        "/api/workspaces",
        json={
            "title": "Contract consulting search",
            "description": "Fractional platform consulting work.",
            "workspace_type": "contract_consulting",
            "preferences": {
                "targetTitles": ["Principal Consultant"],
                "preferredRemoteTypes": ["remote"],
                "targetKeywords": ["platform", "python"],
                "notes": "Prefer high-trust advisory work.",
            },
            "ai_context_summary": "Consulting-oriented positioning.",
            "tags": ["consulting"],
            "metadata": {
                "contextPreferences": {
                    "employmentType": "contract",
                    "preferredIndustries": ["SaaS"],
                    "toneStyle": "consultative",
                }
            },
        },
    )
    assert create_response.status_code == 201
    workspace = create_response.json()
    assert workspace["status"] == "active"
    assert workspace["preferences"]["targetKeywords"] == ["platform", "python"]
    assert workspace["metadata"]["contextPreferences"]["employmentType"] == "contract"

    list_response = workspace_client.get("/api/workspaces")
    assert list_response.status_code == 200
    assert workspace["id"] in [item["id"] for item in list_response.json()]

    update_response = workspace_client.patch(
        f"/api/workspaces/{workspace['id']}",
        json={"status": "paused", "tags": ["consulting", "paused"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "paused"
    assert "paused" in update_response.json()["tags"]

    archive_response = workspace_client.post(
        f"/api/workspaces/{workspace['id']}/archive"
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    active_list = workspace_client.get("/api/workspaces").json()
    assert workspace["id"] not in [item["id"] for item in active_list]

    inactive_list = workspace_client.get(
        "/api/workspaces",
        params={"include_inactive": True},
    ).json()
    assert workspace["id"] in [item["id"] for item in inactive_list]

    reactivate_response = workspace_client.post(
        f"/api/workspaces/{workspace['id']}/reactivate"
    )
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["status"] == "active"
    assert reactivate_response.json()["archived_at"] is None


def test_default_workspace_is_seeded_and_used_for_roles(
    workspace_client: TestClient,
) -> None:
    workspaces = workspace_client.get("/api/workspaces").json()
    assert str(DEFAULT_WORKSPACE_ID) in [item["id"] for item in workspaces]

    role_response = workspace_client.post(
        "/api/roles",
        json={
            "title": "Platform Engineer",
            "company": {"name": "Default Workspace Co"},
            "source": {"source_type": "manual"},
            "status": "found",
        },
    )

    assert role_response.status_code == 201
    assert role_response.json()["workspace_id"] == str(DEFAULT_WORKSPACE_ID)


def test_archived_workspace_is_rejected_for_new_roles(
    workspace_client: TestClient,
) -> None:
    workspace = workspace_client.post(
        "/api/workspaces",
        json={
            "title": "Archived Search",
            "workspace_type": "exploration",
        },
    ).json()
    archive_response = workspace_client.post(
        f"/api/workspaces/{workspace['id']}/archive"
    )
    assert archive_response.status_code == 200

    role_response = workspace_client.post(
        "/api/roles",
        json={
            "workspace_id": workspace["id"],
            "title": "Archived Workspace Role",
            "company": {"name": "Archived Co"},
            "source": {"source_type": "manual"},
            "status": "found",
        },
    )

    assert role_response.status_code == 409


def test_workspace_preferences_affect_stride_input_hash_and_context(
    workspace_client: TestClient,
) -> None:
    python_workspace = workspace_client.post(
        "/api/workspaces",
        json={
            "title": "Python Staff Search",
            "preferences": {"targetKeywords": ["python"]},
            "ai_context_summary": "Python-focused staff search.",
        },
    ).json()
    salesforce_workspace = workspace_client.post(
        "/api/workspaces",
        json={
            "title": "Salesforce Consulting Search",
            "workspace_type": "contract_consulting",
            "preferences": {"targetKeywords": ["salesforce"]},
            "ai_context_summary": "Consulting search with CRM focus.",
        },
    ).json()

    def create_role(workspace_id: str, company_name: str) -> dict:
        response = workspace_client.post(
            "/api/roles",
            json={
                "workspace_id": workspace_id,
                "title": "Platform Engineer",
                "company": {"name": company_name},
                "source": {"source_type": "manual"},
                "raw_description": "Build Python platforms.",
                "status": "found",
            },
        )
        assert response.status_code == 201
        return response.json()

    python_role = create_role(python_workspace["id"], "Python Co")
    salesforce_role = create_role(salesforce_workspace["id"], "Salesforce Co")

    python_eval = workspace_client.post(
        f"/api/roles/{python_role['id']}/evaluations",
        json={},
    ).json()
    salesforce_eval = workspace_client.post(
        f"/api/roles/{salesforce_role['id']}/evaluations",
        json={},
    ).json()

    assert python_eval["workspace_id"] == python_workspace["id"]
    assert salesforce_eval["workspace_id"] == salesforce_workspace["id"]
    assert python_eval["evaluation_input_hash"] != salesforce_eval[
        "evaluation_input_hash"
    ]
    assert python_eval["ats_keywords"] == ["python"]
    assert salesforce_eval["missing_keywords"] == ["salesforce"]
    assert python_eval["raw_evaluation_json"]["workspace"]["id"] == python_workspace["id"]
    assert (
        salesforce_eval["raw_evaluation_json"]["effective_user_context"][
            "target_keywords"
        ]
        == ["salesforce"]
    )
