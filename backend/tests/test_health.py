from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_test_settings() -> Settings:
    return Settings(_env_file=None)


def test_health_check_returns_ok() -> None:
    client = TestClient(create_app(make_test_settings()))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "Careero API",
        "environment": "local",
    }


def test_database_health_returns_ok_when_probe_succeeds(monkeypatch) -> None:
    def check_database_succeeds(settings) -> None:
        assert settings.database_url

    monkeypatch.setattr("app.main.check_database", check_database_succeeds)
    client = TestClient(create_app(make_test_settings()))

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "available",
    }


def test_database_health_returns_unhealthy_when_probe_fails(monkeypatch) -> None:
    def check_database_fails(settings) -> None:
        raise ConnectionError("could not connect with secret://value")

    monkeypatch.setattr("app.main.check_database", check_database_fails)
    client = TestClient(create_app(make_test_settings()))

    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unhealthy",
        "database": "unavailable",
    }
