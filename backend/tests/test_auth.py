from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.main import create_app
from app.models import AuthSession, JobSource, User, Workspace
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.auth import hash_password, hash_session_token, verify_password


PASSWORD = "correct horse battery staple"


@pytest.fixture
def auth_client(db_session: Session) -> Generator[TestClient, None, None]:
    settings = Settings(
        _env_file=None,
        enable_password_auth=True,
        allow_registration=True,
        password_min_length=8,
        auth_cookie_secure=False,
    )
    app = create_app(settings)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _register(
    client: TestClient,
    *,
    first_name: str = "Matthew",
    last_name: str = "Coleman",
    email: str = "matthew@example.com",
    password: str = PASSWORD,
) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    assert "httponly" in response.headers["set-cookie"].lower()
    return response.json()


def _logout(client: TestClient) -> None:
    response = client.post("/api/auth/logout")
    assert response.status_code == 204


def test_password_hashing_does_not_store_plaintext() -> None:
    password_hash = hash_password(PASSWORD)

    assert PASSWORD not in password_hash
    assert password_hash.startswith("$argon2id$")
    assert verify_password(PASSWORD, password_hash)
    assert not verify_password("wrong password", password_hash)


def test_registration_creates_user_workspace_sources_and_session(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    payload = _register(auth_client)
    user_id = UUID(payload["id"])
    user = db_session.get(User, user_id)

    assert user is not None
    assert user.password_hash is not None
    assert PASSWORD not in user.password_hash
    assert user.first_name == "Matthew"
    assert user.last_name == "Coleman"
    assert user.display_name == "Matthew Coleman"
    assert user.email_normalized == "matthew@example.com"
    assert db_session.scalar(
        select(func.count()).select_from(Workspace).where(Workspace.user_id == user.id)
    ) == 1
    assert db_session.scalar(
        select(func.count()).select_from(JobSource).where(JobSource.user_id == user.id)
    ) > 0
    assert "password" not in payload
    assert "password_hash" not in payload

    session = db_session.scalar(select(AuthSession).where(AuthSession.user_id == user.id))
    assert session is not None
    raw_cookie = auth_client.cookies.get("careero_session")
    assert raw_cookie
    assert session.session_token_hash == hash_session_token(raw_cookie)
    assert session.session_token_hash != raw_cookie


def test_duplicate_email_is_rejected(auth_client: TestClient) -> None:
    _register(auth_client)
    _logout(auth_client)

    duplicate_email = auth_client.post(
        "/api/auth/register",
        json={
            "email": "Matthew@Example.com",
            "firstName": "Other",
            "lastName": "Person",
            "password": PASSWORD,
        },
    )
    assert duplicate_email.status_code == 409


def test_registration_accepts_snake_case_name_payload(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/register",
        json={
            "first_name": "Snake",
            "last_name": "Case",
            "email": "snake@example.com",
            "password": PASSWORD,
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["firstName"] == "Snake"
    assert response.json()["lastName"] == "Case"


def test_login_succeeds_with_email(auth_client: TestClient) -> None:
    _register(auth_client)
    _logout(auth_client)

    email_login = auth_client.post(
        "/api/auth/login",
        json={"email": "matthew@example.com", "password": PASSWORD},
    )
    assert email_login.status_code == 200
    assert email_login.json()["email"] == "matthew@example.com"
    assert email_login.json()["firstName"] == "Matthew"
    assert email_login.json()["lastName"] == "Coleman"


def test_login_rejects_wrong_password_with_generic_error(auth_client: TestClient) -> None:
    _register(auth_client)
    _logout(auth_client)

    response = auth_client.post(
        "/api/auth/login",
        json={"email": "matthew@example.com", "password": "not the password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_inactive_user(auth_client: TestClient, db_session: Session) -> None:
    payload = _register(auth_client)
    _logout(auth_client)
    user = db_session.get(User, UUID(payload["id"]))
    assert user is not None
    user.account_status = "disabled"
    db_session.commit()

    response = auth_client.post(
        "/api/auth/login",
        json={"email": "matthew@example.com", "password": PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_and_logout_use_revocable_cookie_session(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    payload = _register(auth_client)

    me = auth_client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["id"] == payload["id"]

    logout = auth_client.post("/api/auth/logout")
    assert logout.status_code == 204
    session = db_session.scalar(select(AuthSession))
    assert session is not None
    assert session.revoked_at is not None

    after_logout = auth_client.get("/api/auth/me")
    assert after_logout.status_code == 401


def test_me_and_protected_endpoint_reject_unauthenticated_request(
    auth_client: TestClient,
) -> None:
    assert auth_client.get("/api/auth/me").status_code == 401
    assert auth_client.get("/api/workspaces").status_code == 401


def test_protected_endpoint_uses_authenticated_user_not_seeded_local_user(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    payload = _register(auth_client, first_name="Owner", last_name="One", email="owner@example.com")

    response = auth_client.get("/api/workspaces")

    assert response.status_code == 200
    workspace_ids = {item["id"] for item in response.json()}
    assert str(DEFAULT_WORKSPACE_ID) not in workspace_ids
    assert all(item["user_id"] == payload["id"] for item in response.json())


def test_user_cannot_access_another_users_workspace(db_session: Session) -> None:
    settings = Settings(
        _env_file=None,
        enable_password_auth=True,
        allow_registration=True,
        password_min_length=8,
    )
    app = create_app(settings)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as user_a, TestClient(app) as user_b:
        _register(user_a, first_name="Owner", last_name="A", email="owner-a@example.com")
        workspace = user_a.get("/api/workspaces").json()[0]
        _register(user_b, first_name="Owner", last_name="B", email="owner-b@example.com")

        cross_user = user_b.get(f"/api/workspaces/{workspace['id']}")

        assert cross_user.status_code == 404
    app.dependency_overrides.clear()
