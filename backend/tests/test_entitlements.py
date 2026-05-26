from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.entitlements import get_current_entitlements


def test_current_entitlements_returns_local_free_plan() -> None:
    entitlements = get_current_entitlements()

    assert entitlements.plan_id == "local_free"
    assert entitlements.plan_display_name == "Local Free"
    assert entitlements.billing_status == "not_configured"
    assert entitlements.payment_provider == "none"


def test_essential_workflow_features_are_enabled() -> None:
    response = get_current_entitlements()
    enabled = {item.key for item in response.entitlements if item.enabled}

    assert "opportunity_capture" in enabled
    assert "workspace_organization" in enabled
    assert "application_workflow" in enabled
    assert "deterministic_compass" in enabled
    assert "local_data_export" in enabled


def test_no_employer_sponsored_entitlement_exists() -> None:
    response = get_current_entitlements()
    serialized = response.model_dump_json()

    assert "employer_sponsored_ranking" in response.unavailable_future_features
    assert "sponsored_recommendations" in response.unavailable_future_features
    assert '"employer_sponsored_ranking","enabled":true' not in serialized
    assert '"sponsored_recommendations","enabled":true' not in serialized


def test_current_entitlements_endpoint_shape() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    response = client.get("/api/entitlements/current")

    assert response.status_code == 200
    body = response.json()
    assert body["plan_id"] == "local_free"
    assert body["billing_status"] == "not_configured"
    assert body["payment_provider"] == "none"
    assert "No payment provider is configured." in body["monetization_guardrails"]
