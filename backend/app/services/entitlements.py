from __future__ import annotations

from app.schemas.entitlements import CurrentEntitlementsResponse


ESSENTIAL_LOCAL_ENTITLEMENTS = [
    {
        "key": "opportunity_capture",
        "enabled": True,
        "category": "essential_workflow",
        "description": "Capture and organize opportunities locally.",
    },
    {
        "key": "workspace_organization",
        "enabled": True,
        "category": "essential_workflow",
        "description": "Use local workspaces/search tracks.",
    },
    {
        "key": "application_workflow",
        "enabled": True,
        "category": "essential_workflow",
        "description": "Track applications, states, notes, links, reminders, and interviews.",
    },
    {
        "key": "deterministic_compass",
        "enabled": True,
        "category": "essential_guidance",
        "description": "Use deterministic local COMPASS evaluation where available.",
    },
    {
        "key": "local_data_export",
        "enabled": True,
        "category": "data_ownership",
        "description": "Export current local-user data as JSON.",
    },
    {
        "key": "local_lifecycle_request_tracking",
        "enabled": True,
        "category": "data_ownership",
        "description": "Record non-destructive local lifecycle requests.",
    },
    {
        "key": "local_ai_usage_visibility",
        "enabled": True,
        "category": "ai_transparency",
        "description": "View local AI usage metadata without billing claims.",
    },
]

UNAVAILABLE_FUTURE_FEATURES = [
    "paid_ai_quota_enforcement",
    "credit_wallet",
    "billing_provider_checkout",
    "subscriptions",
    "invoices",
    "hosted_collaboration",
    "production_multi_tenant_identity",
    "cloud_backup_restore",
    "employer_sponsored_ranking",
    "sponsored_recommendations",
]

MONETIZATION_GUARDRAILS = [
    "Careero preserves a useful free/local baseline.",
    "Essential local organization is not locked behind a paid tier.",
    "No payment provider is configured.",
    "No upgrade, checkout, subscription, invoice, or credit wallet exists.",
    "Employer-sponsored ranking and hidden sponsored recommendations are prohibited.",
    "Future paid boundaries must remain job-seeker-first and transparent.",
]


def get_current_entitlements() -> CurrentEntitlementsResponse:
    return CurrentEntitlementsResponse(
        plan_id="local_free",
        plan_display_name="Local Free",
        billing_status="not_configured",
        payment_provider="none",
        entitlements=ESSENTIAL_LOCAL_ENTITLEMENTS,
        feature_limits=[
            {
                "key": "local_ai_session_attempt_cap",
                "value": "configured_by_environment",
                "description": "Existing local AI session caps may apply outside billing.",
            },
            {
                "key": "paid_usage_enforcement",
                "value": None,
                "description": "No paid quota or credit enforcement exists.",
            },
        ],
        unavailable_future_features=UNAVAILABLE_FUTURE_FEATURES,
        monetization_guardrails=MONETIZATION_GUARDRAILS,
        local_first_note=(
            "The local_free plan is a local-first boundary model only. It does "
            "not configure billing, collect payment details, or enforce paid tiers."
        ),
        metadata={"schema_version": "careero.local_entitlements.v1"},
    )
