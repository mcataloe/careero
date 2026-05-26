from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.roles import get_ai_usage_service, get_role_parsing_service
from app.database import get_db
from app.main import create_app
from app.models import Role
from app.schemas.role_parsing import ParsedRole, RoleParseResponse
from app.seed import seed_local_data


def opportunity_payload(company_name: str = "Example Company") -> dict:
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
            "parseWarnings": ["Review compensation."],
        },
        "status": "found",
        "date_found": "2026-05-13",
        "date_posted": "2026-05-01",
    }


@pytest.fixture
def opportunity_api_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_opportunity_routes_create_list_detail_update_intelligence_and_archive(
    db_session: Session,
    opportunity_api_client: TestClient,
) -> None:
    create_response = opportunity_api_client.post(
        "/api/opportunities",
        json=opportunity_payload(),
    )
    assert create_response.status_code == 201
    opportunity_id = create_response.json()["id"]
    opportunity_uuid = UUID(opportunity_id)

    list_response = opportunity_api_client.get("/api/opportunities")
    assert list_response.status_code == 200
    assert [opportunity["id"] for opportunity in list_response.json()] == [
        opportunity_id
    ]

    detail_response = opportunity_api_client.get(
        f"/api/opportunities/{opportunity_id}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "Senior Backend Engineer"

    update_response = opportunity_api_client.patch(
        f"/api/opportunities/{opportunity_id}",
        json={
            "status": "interested",
            "remote_type": "remote",
            "normalized_description": "Updated normalized description",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "interested"
    assert update_response.json()["remote_type"] == "remote"

    intelligence_response = opportunity_api_client.post(
        f"/api/opportunities/{opportunity_id}/opportunity-intelligence"
    )
    assert intelligence_response.status_code == 200
    assert (
        intelligence_response.json()["parse_metadata"]["opportunityIntelligence"][
            "version"
        ]
        == "opportunity-intelligence.v1"
    )

    roles_compat_response = opportunity_api_client.get(f"/api/roles/{opportunity_id}")
    assert roles_compat_response.status_code == 200
    assert roles_compat_response.json()["id"] == opportunity_id

    delete_response = opportunity_api_client.delete(
        f"/api/opportunities/{opportunity_id}"
    )
    assert delete_response.status_code == 204

    archived_role = db_session.get(Role, opportunity_uuid)
    assert archived_role is not None
    assert archived_role.status == "archived"
    assert archived_role.deleted_at is not None

    assert opportunity_api_client.get("/api/opportunities").json() == []


def test_opportunity_parse_route_uses_role_backed_parser() -> None:
    app = create_app()

    class FakeService:
        def parse(self, payload):
            return RoleParseResponse(
                parsed=ParsedRole(roleTitle="Engineer", company="Acme"),
                metadata={"parserVersion": "role_parser_v1", "model": "gpt-5-mini"},
            )

    class FakeUsageService:
        class FakeDb:
            def commit(self):
                return None

        db = FakeDb()

        def current_user(self):
            class User:
                id = "00000000-0000-4000-8000-000000000001"

            return User()

        def record_event(self, payload):
            return None

    app.dependency_overrides[get_role_parsing_service] = lambda: FakeService()
    app.dependency_overrides[get_ai_usage_service] = lambda: FakeUsageService()
    with TestClient(app) as client:
        response = client.post(
            "/api/opportunities/parse",
            json={"rawText": "Engineer at Acme"},
        )
        roles_response = client.post(
            "/api/roles/parse",
            json={"rawText": "Engineer at Acme"},
        )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["parsed"]["roleTitle"] == "Engineer"
    assert roles_response.status_code == 200
    assert roles_response.json()["parsed"]["roleTitle"] == "Engineer"
