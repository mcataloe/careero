import json

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def make_client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


def assert_database_available(settings: Settings) -> None:
    assert settings.database_url


def test_local_readiness_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.productization_readiness.check_database",
        assert_database_available,
    )
    client = make_client(make_settings(environment="local"))

    response = client.get("/api/productization/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["environment"] == "local"
    assert body["readiness_stage"] == "local_poc"
    assert body["production_ready"] is False
    assert body["local_first_status"] == "active_local_first"
    assert body["database_health"] == "available"
    assert body["auth_status"]["status"] == "not_implemented"
    assert body["tenant_boundary_prep_status"]["status"] == "local_boundary_prep"
    assert body["billing_status"]["status"] == "not_implemented"
    assert body["export_delete_status"]["status"] == "local_export_and_request_tracking"


def test_production_like_readiness_response_reports_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.productization_readiness.check_database",
        assert_database_available,
    )
    client = make_client(make_settings(environment="production"))

    response = client.get("/api/productization/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["environment"] == "production"
    assert body["readiness_stage"] == "production_blocked"
    assert body["production_ready"] is False
    assert body["deployment_status"]["status"] == "production_controls_missing"
    assert any("production-like environment" in item for item in body["known_blockers"])


def test_readiness_response_does_not_leak_secrets(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.productization_readiness.check_database",
        assert_database_available,
    )
    settings = make_settings(
        database_url="postgresql://secret_user:secret_password@localhost:5432/careero",
        openai_api_key="sk-secret-readiness-test",
    )
    client = make_client(settings)

    response = client.get("/api/productization/readiness")

    assert response.status_code == 200
    serialized = json.dumps(response.json())
    assert "secret_user" not in serialized
    assert "secret_password" not in serialized
    assert "sk-secret-readiness-test" not in serialized
    assert "postgresql://" not in serialized
    assert response.json()["ai_feature_flags"]["provider_key_configured"] is True


def test_ai_feature_flags_are_represented(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.productization_readiness.check_database",
        assert_database_available,
    )
    settings = make_settings(
        enable_ai_role_parsing=True,
        enable_ai_evaluations=True,
        enable_ai_resume_generation=False,
        enable_ai_cover_letter_generation=True,
        max_ai_evaluations_per_session=7,
    )
    client = make_client(settings)

    response = client.get("/api/productization/readiness")

    assert response.status_code == 200
    assert response.json()["ai_feature_flags"] == {
        "role_parsing_enabled": True,
        "compass_enrichment_enabled": True,
        "resume_generation_enabled": False,
        "cover_letter_generation_enabled": True,
        "provider_key_configured": False,
        "local_session_attempt_cap": 7,
        "durable_metering_status": "local_usage_events",
    }


def test_endpoint_shape_is_stable(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.productization_readiness.check_database",
        assert_database_available,
    )
    client = make_client(make_settings())

    response = client.get("/api/productization/readiness")

    assert response.status_code == 200
    assert set(response.json().keys()) == {
        "environment",
        "readiness_stage",
        "production_ready",
        "local_first_status",
        "local_workflow_readiness",
        "database_health",
        "ai_feature_flags",
        "auth_status",
        "tenant_boundary_prep_status",
        "billing_status",
        "export_delete_status",
        "retention_status",
        "durable_usage_metering_status",
        "deployment_status",
        "hosted_collaboration_status",
        "marketplace_employer_side_status",
        "known_blockers",
        "production_readiness_statement",
    }
    assert set(response.json()["local_workflow_readiness"].keys()) == {
        "core_workflow",
        "application_workflow",
        "artifact_lifecycle",
        "integrations",
        "automation",
    }
