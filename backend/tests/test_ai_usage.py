from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.main import create_app
from app.models import User
from app.schemas.ai_usage import AIUsageEventCreate
from app.seed import seed_default_job_sources, seed_local_data
from app.services.ai_usage import AIUsageService, content_hash
from app.services.current_user import CurrentUserContext


@contextmanager
def _api_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app(Settings(_env_file=None))

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_usage_event_persists_safe_completed_metadata(db_session: Session) -> None:
    user, _ = seed_local_data(db_session)
    event = AIUsageService(db_session).record_event(
        AIUsageEventCreate(
            user_id=user.id,
            feature="parse_opportunity",
            event_type="completed",
            provider="openai",
            model="gpt-5-mini",
            input_token_estimate=10,
            output_token_estimate=8,
            latency_ms=123,
            content_hash=content_hash("private raw job description"),
        )
    )
    db_session.commit()
    db_session.refresh(event)

    assert event.feature == "parse_opportunity"
    assert event.event_type == "completed"
    assert event.input_token_estimate == 10
    assert event.content_hash.startswith("sha256:")
    assert event.content_hash != "private raw job description"


def test_usage_event_sanitizes_private_content_and_secrets(db_session: Session) -> None:
    user, _ = seed_local_data(db_session)
    event = AIUsageService(db_session).record_event(
        AIUsageEventCreate(
            user_id=user.id,
            feature="compass_enrichment",
            event_type="failed",
            error_class="TimeoutError: sk-secret123",
            metadata={
                "raw_prompt": "resume says private compensation strategy",
                "api_key": "sk-secret123",
                "safe_status": "failed",
            },
        )
    )
    db_session.commit()
    db_session.refresh(event)

    serialized = str(event.event_metadata)
    assert "sk-secret123" not in serialized
    assert "private compensation strategy" not in serialized
    assert "api_key" not in serialized
    assert event.event_metadata == {"safe_status": "failed"}
    assert event.error_class == "TimeoutError"


def test_usage_endpoint_is_scoped_to_current_user(db_session: Session) -> None:
    user_a, _ = seed_local_data(db_session)
    user_b = User(
        id=uuid4(),
        email="usage-other@careero.local",
        display_name="Usage Other",
    )
    db_session.add(user_b)
    db_session.commit()
    seed_default_job_sources(db_session, user_b)
    AIUsageService(db_session).record_event(
        AIUsageEventCreate(
            user_id=user_a.id,
            feature="resume_artifact",
            event_type="completed",
        )
    )
    AIUsageService(
        db_session,
        current_user_context=CurrentUserContext(user_id=user_b.id, mode="test"),
    ).record_event(
        AIUsageEventCreate(
            user_id=user_b.id,
            feature="cover_letter_artifact",
            event_type="completed",
        )
    )
    db_session.commit()

    with _api_client(db_session) as client:
        response = client.get("/api/usage/ai")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total_events"] == 1
    assert body["events"][0]["feature"] == "resume_artifact"
    assert "cover_letter_artifact" not in str(body)


def test_usage_endpoint_empty_state(db_session: Session) -> None:
    seed_local_data(db_session)

    with _api_client(db_session) as client:
        response = client.get("/api/usage/ai")

    assert response.status_code == 200
    assert response.json()["events"] == []
    assert response.json()["summary"]["total_events"] == 0
