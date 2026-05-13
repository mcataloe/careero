from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_database_health_uses_configured_database(migrated_database: str) -> None:
    settings = Settings(_env_file=None, database_url=migrated_database)
    client = TestClient(create_app(settings))

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "available",
    }
