from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, User
from app.seed import DEFAULT_LOCAL_USER_ID, seed_local_data


@pytest.fixture
def activity_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_activity_log_lists_and_filters_default_user_entries(
    activity_client: TestClient,
    db_session: Session,
) -> None:
    role_id = uuid4()
    evaluation_id = uuid4()
    other_user = User(email="activity-other@careero.local", display_name="Other")
    db_session.add(other_user)
    db_session.flush()
    db_session.add_all(
        [
            ActivityLog(
                user_id=DEFAULT_LOCAL_USER_ID,
                entity_type="role",
                entity_id=role_id,
                action="role.created",
                details={"title": "Example"},
            ),
            ActivityLog(
                user_id=DEFAULT_LOCAL_USER_ID,
                entity_type="stride_evaluation",
                entity_id=evaluation_id,
                action="stride_evaluation.completed",
                details={"role_id": str(role_id)},
            ),
            ActivityLog(
                user_id=other_user.id,
                entity_type="stride_evaluation",
                entity_id=uuid4(),
                action="stride_evaluation.completed",
                details={},
            ),
        ]
    )
    db_session.commit()

    response = activity_client.get(
        "/api/activity-log",
        params={
            "entity_type": "stride_evaluation",
            "entity_id": str(evaluation_id),
            "action": "stride_evaluation.completed",
        },
    )

    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 1
    assert entries[0]["entity_id"] == str(evaluation_id)
    assert entries[0]["action"] == "stride_evaluation.completed"
    assert entries[0]["details"]["role_id"] == str(role_id)


def test_activity_log_limit_validation(activity_client: TestClient) -> None:
    assert activity_client.get("/api/activity-log", params={"limit": 0}).status_code == 422
    assert activity_client.get("/api/activity-log", params={"limit": 201}).status_code == 422


def test_activity_log_empty_results(activity_client: TestClient) -> None:
    response = activity_client.get(
        "/api/activity-log",
        params={"entity_type": "missing"},
    )

    assert response.status_code == 200
    assert response.json() == []
