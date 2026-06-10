from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, Company, Role
from app.seed import DEFAULT_LOCAL_USER_ID, seed_local_data


@pytest.fixture
def role_api_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def role_payload(company_name: str = "Example Company") -> dict:
    return {
        "title": "Senior Backend Engineer",
        "company": {
            "name": company_name,
            "website_url": "https://example.com",
        },
        "source": {
            "source_type": "linkedin_manual",
        },
        "job_url": "https://www.linkedin.com/jobs/view/example",
        "location": "Chicago, IL",
        "remote_type": "hybrid",
        "compensation_min": "120000.00",
        "compensation_max": "150000.00",
        "compensation_currency": "usd",
        "raw_description": "Raw pasted job description",
        "normalized_description": "Normalized job description",
        "parse_metadata": {
            "parserVersion": "role_parser_v1",
            "aiModel": "gpt-5-mini",
            "parseWarnings": ["Review compensation."],
            "confidence": {"roleTitle": 0.93},
            "userEditedFields": ["title"],
        },
        "status": "found",
        "date_found": "2026-05-13",
        "date_posted": "2026-05-01",
    }


def test_create_role_with_new_company_and_source_type(role_api_client: TestClient) -> None:
    response = role_api_client.post("/api/roles", json=role_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Senior Backend Engineer"
    assert body["company"]["name"] == "Example Company"
    assert body["source"]["source_type"] == "linkedin_manual"
    assert body["job_url"] == "https://www.linkedin.com/jobs/view/example"
    assert body["compensation_currency"] == "USD"
    assert body["parse_metadata"]["parserVersion"] == "role_parser_v1"
    assert body["parse_metadata"]["userEditedFields"] == ["title"]


def test_create_role_reuses_company_by_case_insensitive_name(
    role_api_client: TestClient,
    db_session: Session,
) -> None:
    first = role_api_client.post("/api/roles", json=role_payload("Acme"))
    second = role_api_client.post("/api/roles", json=role_payload("acme"))

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["company_id"] == second.json()["company_id"]

    company_count = db_session.scalar(
        select(func.count()).select_from(Company).where(
            Company.user_id == DEFAULT_LOCAL_USER_ID
        )
    )
    assert company_count == 1


def test_list_get_update_and_archive_role(
    role_api_client: TestClient,
    db_session: Session,
) -> None:
    create_response = role_api_client.post("/api/roles", json=role_payload())
    assert create_response.status_code == 201
    role_id = create_response.json()["id"]
    role_uuid = UUID(role_id)

    list_response = role_api_client.get("/api/roles")
    assert list_response.status_code == 200
    assert [role["id"] for role in list_response.json()] == [role_id]

    detail_response = role_api_client.get(f"/api/roles/{role_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == role_id

    update_response = role_api_client.patch(
        f"/api/roles/{role_id}",
        json={
            "status": "interested",
            "remote_type": "remote",
            "normalized_description": "Updated normalized description",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "interested"
    assert update_response.json()["remote_type"] == "remote"

    delete_response = role_api_client.delete(f"/api/roles/{role_id}")
    assert delete_response.status_code == 204

    archived_role = db_session.get(Role, role_uuid)
    assert archived_role is not None
    assert archived_role.status == "archived"
    assert archived_role.deleted_at is not None

    list_after_archive = role_api_client.get("/api/roles")
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []

    detail_after_archive = role_api_client.get(f"/api/roles/{role_id}")
    assert detail_after_archive.status_code == 404

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == role_uuid)
        )
    )
    assert actions == [
        "opportunity.created",
        "opportunity.updated",
        "opportunity.archived",
    ]
