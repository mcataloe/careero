from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, Role, User
from app.schemas.account_lifecycle import AccountLifecycleRequestCreate
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.seed import seed_default_job_sources, seed_local_data
from app.services.account_lifecycle import (
    AccountLifecycleRequestNotFoundError,
    AccountLifecycleService,
)
from app.services.current_user import CurrentUserContext
from app.services.roles import RoleService


@pytest.fixture
def seeded_session(db_session: Session) -> Session:
    seed_local_data(db_session)
    return db_session


@contextmanager
def _api_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app(Settings(_env_file=None))

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _create_role(db_session: Session) -> Role:
    return RoleService(db_session).create_role(
        RoleCreate(
            title="Lifecycle Sentinel Role",
            company=CompanyLookup(name="Lifecycle Co"),
            source=SourceLookup(source_type="manual"),
            raw_description="Private role text that must not enter activity logs.",
        )
    )


def test_create_and_list_lifecycle_request(seeded_session: Session) -> None:
    service = AccountLifecycleService(seeded_session)

    request = service.create_request(
        AccountLifecycleRequestCreate(
            request_type="data_export",
            request_reason="I want a local copy.",
            request_metadata={"surface": "settings", "private": {"ignored": True}},
        )
    )
    requests = service.list_requests()

    assert request.request_type == "data_export"
    assert request.status == "requested"
    assert requests[0].id == request.id
    assert requests[0].request_metadata == {"surface": "settings"}


def test_cancel_lifecycle_request(seeded_session: Session) -> None:
    service = AccountLifecycleService(seeded_session)
    request = service.create_request(
        AccountLifecycleRequestCreate(request_type="retention_review")
    )

    canceled = service.cancel_request(request.id)

    assert canceled.status == "canceled"
    assert canceled.canceled_at is not None


def test_cannot_cancel_another_users_lifecycle_request(db_session: Session) -> None:
    user_a, _ = seed_local_data(db_session)
    user_b = User(
        id=uuid4(),
        email="lifecycle-other@careero.local",
        first_name="Lifecycle",
        last_name="Other",
        display_name="Lifecycle Other",
    )
    db_session.add(user_b)
    db_session.commit()
    seed_default_job_sources(db_session, user_b)
    context_a = CurrentUserContext(user_id=user_a.id, mode="test")
    context_b = CurrentUserContext(user_id=user_b.id, mode="test")
    request_b = AccountLifecycleService(
        db_session,
        current_user_context=context_b,
    ).create_request(AccountLifecycleRequestCreate(request_type="data_export"))

    with pytest.raises(AccountLifecycleRequestNotFoundError):
        AccountLifecycleService(
            db_session,
            current_user_context=context_a,
        ).cancel_request(request_b.id)

    assert (
        AccountLifecycleService(db_session, current_user_context=context_b)
        .list_requests()[0]
        .status
        == "requested"
    )


def test_deletion_request_does_not_delete_user_data(seeded_session: Session) -> None:
    role = _create_role(seeded_session)
    request = AccountLifecycleService(seeded_session).create_request(
        AccountLifecycleRequestCreate(
            request_type="account_deletion",
            deletion_confirmation="record deletion request",
        )
    )

    assert request.request_type == "account_deletion"
    assert seeded_session.get(Role, role.id) is not None
    assert seeded_session.get(Role, role.id).deleted_at is None


def test_activity_log_omits_private_reason_content(seeded_session: Session) -> None:
    AccountLifecycleService(seeded_session).create_request(
        AccountLifecycleRequestCreate(
            request_type="account_deletion",
            request_reason="Delete this because my private compensation strategy changed.",
            deletion_confirmation="record deletion request",
        )
    )

    log = seeded_session.scalar(
        select(ActivityLog).where(ActivityLog.entity_type == "account_lifecycle_request")
    )

    assert log is not None
    assert log.action == "account_lifecycle.requested"
    assert "request_type" in log.details
    assert "private compensation strategy" not in str(log.details)
    assert log.details["deletion_enforced"] is False


def test_lifecycle_api_create_list_and_cancel(seeded_session: Session) -> None:
    with _api_client(seeded_session) as client:
        created = client.post(
            "/api/account/lifecycle-requests",
            json={"request_type": "data_export"},
        )
        listed = client.get("/api/account/lifecycle-requests")
        canceled = client.post(
            f"/api/account/lifecycle-requests/{created.json()['id']}/cancel"
        )

    assert created.status_code == 201
    assert created.json()["message"].startswith("Export request recorded locally")
    assert listed.status_code == 200
    assert listed.json()["requests"][0]["id"] == created.json()["id"]
    assert canceled.status_code == 200
    assert canceled.json()["status"] == "canceled"
