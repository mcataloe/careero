from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.seed import seed_local_data


@pytest.fixture
def resume_source_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def source_payload(name: str = "Master Resume") -> dict:
    return {
        "name": name,
        "source_type": "master_resume",
        "version_label": "v1",
        "raw_text": "Senior platform engineer with Python and PostgreSQL experience.",
        "normalized_summary": "Senior platform engineer focused on Python systems.",
        "is_active": True,
    }


def test_create_list_and_get_active_resume_source(
    resume_source_client: TestClient,
) -> None:
    create_response = resume_source_client.post(
        "/api/resume-sources",
        json=source_payload(),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Master Resume"
    assert created["source_type"] == "master_resume"
    assert created["active_version"]["version_label"] == "v1"
    assert created["active_version"]["is_active"] is True

    list_response = resume_source_client.get("/api/resume-sources")
    assert list_response.status_code == 200
    assert [source["id"] for source in list_response.json()] == [created["id"]]

    active_response = resume_source_client.get("/api/resume-sources/active")
    assert active_response.status_code == 200
    assert active_response.json()["source"]["id"] == created["id"]
    assert active_response.json()["version"]["id"] == created["active_version"]["id"]


def test_create_new_version_and_activate_it(
    resume_source_client: TestClient,
) -> None:
    create_response = resume_source_client.post(
        "/api/resume-sources",
        json=source_payload(),
    )
    source = create_response.json()
    old_version_id = source["active_version"]["id"]

    version_response = resume_source_client.post(
        f"/api/resume-sources/{source['id']}/versions",
        json={
            "version_label": "v2",
            "raw_text": "Staff platform engineer with Python, PostgreSQL, and AWS.",
            "normalized_summary": "Staff platform engineer focused on backend platforms.",
            "is_active": False,
        },
    )
    assert version_response.status_code == 201
    new_version = version_response.json()
    assert new_version["is_active"] is False

    activate_response = resume_source_client.post(
        f"/api/resume-sources/{source['id']}/versions/{new_version['id']}/activate"
    )
    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True

    active_response = resume_source_client.get("/api/resume-sources/active")
    assert active_response.status_code == 200
    assert active_response.json()["version"]["id"] == new_version["id"]
    assert active_response.json()["version"]["id"] != old_version_id

    list_response = resume_source_client.get("/api/resume-sources")
    listed = list_response.json()[0]
    assert listed["active_version"]["id"] == new_version["id"]
    assert listed["latest_version"]["id"] == new_version["id"]


def test_update_resume_source_metadata(resume_source_client: TestClient) -> None:
    create_response = resume_source_client.post(
        "/api/resume-sources",
        json=source_payload(),
    )
    source = create_response.json()

    update_response = resume_source_client.patch(
        f"/api/resume-sources/{source['id']}",
        json={"name": "Updated Profile", "source_type": "profile"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Profile"
    assert update_response.json()["source_type"] == "profile"


def test_get_active_resume_source_returns_404_when_missing(
    resume_source_client: TestClient,
) -> None:
    response = resume_source_client.get("/api/resume-sources/active")

    assert response.status_code == 404
