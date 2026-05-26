import re
from collections.abc import Callable

from app.config import Settings
from app.database import check_database
from app.schemas.productization import (
    AiFeatureFlags,
    CapabilityReadiness,
    LocalWorkflowReadiness,
    ProductizationReadinessResponse,
    ReadinessStage,
)

DatabaseChecker = Callable[[Settings], None]

PRODUCTION_ENVIRONMENTS = {"prod", "production"}
PRIVATE_BETA_ENVIRONMENTS = {
    "beta",
    "hosted",
    "preprod",
    "private_beta",
    "staging",
}
LOCAL_ENVIRONMENTS = {"dev", "development", "local", "test"}


def _safe_environment_name(environment: str) -> str:
    normalized = environment.strip().lower().replace("-", "_")
    if re.fullmatch(r"[a-z0-9_]{1,64}", normalized):
        return normalized
    return "custom"


def _is_production_like(environment: str) -> bool:
    return environment in PRODUCTION_ENVIRONMENTS | PRIVATE_BETA_ENVIRONMENTS


def _readiness_stage(environment: str) -> ReadinessStage:
    if environment in PRODUCTION_ENVIRONMENTS:
        return "production_blocked"
    if environment in PRIVATE_BETA_ENVIRONMENTS:
        return "private_beta_blocked"
    if environment in LOCAL_ENVIRONMENTS:
        return "local_poc"
    return "local_beta_blocked"


def _database_health(
    settings: Settings,
    database_checker: DatabaseChecker,
) -> str:
    try:
        database_checker(settings)
    except Exception:
        return "unavailable"
    return "available"


def _capability(status: str, implemented: bool, detail: str) -> CapabilityReadiness:
    return CapabilityReadiness(
        status=status,
        implemented=implemented,
        detail=detail,
    )


def get_productization_readiness(
    settings: Settings,
    database_checker: DatabaseChecker | None = None,
) -> ProductizationReadinessResponse:
    database_checker = database_checker or check_database
    environment = _safe_environment_name(settings.environment)
    stage = _readiness_stage(environment)
    database_health = _database_health(settings, database_checker)
    production_like = _is_production_like(environment)

    known_blockers = [
        "Production authentication is not implemented.",
        "Production authorization and tenant isolation are not implemented.",
        "Billing, subscriptions, invoices, checkout, and payment flows are not implemented.",
        "Data export, account deletion, and retention enforcement are not implemented.",
        "Durable AI usage metering and cost controls are not implemented.",
        "Production deployment architecture, monitoring, backup, restore, and incident response are not implemented.",
        "Hosted collaboration and employer-side marketplace capabilities are not implemented.",
        "Artifact lifecycle UX remains incomplete for production or paid use.",
    ]
    if database_health != "available":
        known_blockers.append(
            "Database health is not currently available from the local readiness probe."
        )
    if production_like:
        known_blockers.insert(
            0,
            "A production-like environment is configured, but required production controls are missing.",
        )

    deployment_status = (
        _capability(
            "production_controls_missing",
            False,
            "This environment is production-like, but Careero has no production deployment gate implementation.",
        )
        if production_like
        else _capability(
            "local_only",
            True,
            "Local scripts and health checks exist; cloud deployment remains future.",
        )
    )

    return ProductizationReadinessResponse(
        environment=environment,
        readiness_stage=stage,
        production_ready=False,
        local_first_status=(
            "active_local_first"
            if environment in LOCAL_ENVIRONMENTS
            else "local_first_only_not_hosted_ready"
        ),
        local_workflow_readiness=LocalWorkflowReadiness(
            core_workflow=_capability(
                "local_available",
                True,
                "Manual intake, local persistence, COMPASS foundations, applications, and analytics exist.",
            ),
            application_workflow=_capability(
                "local_available",
                True,
                "Application workflow records are local-first and do not include hosted reminders or external notifications.",
            ),
            artifact_lifecycle=_capability(
                "incomplete",
                False,
                "Generation foundations exist, but production artifact review, approval, submitted tracking, and frontend export workflow remain incomplete.",
            ),
            integrations=_capability(
                "local_only",
                False,
                "Backend local artifact export exists; OAuth, cloud sync, browser intake, and external account mutation remain future.",
            ),
            automation=_capability(
                "local_guardrails_only",
                True,
                "Suggestions and approval logs are local; external actions remain disabled.",
            ),
        ),
        database_health=database_health,
        ai_feature_flags=AiFeatureFlags(
            role_parsing_enabled=settings.enable_ai_role_parsing,
            compass_enrichment_enabled=settings.enable_ai_evaluations,
            resume_generation_enabled=settings.enable_ai_resume_generation,
            cover_letter_generation_enabled=settings.enable_ai_cover_letter_generation,
            provider_key_configured=bool(settings.openai_api_key),
            local_session_attempt_cap=settings.max_ai_evaluations_per_session,
            durable_metering_status="not_implemented",
        ),
        auth_status=_capability(
            "not_implemented",
            False,
            "Auth-provider choice is deferred; no login, signup, OAuth, sessions, JWTs, or production auth exist.",
        ),
        tenant_boundary_prep_status=_capability(
            "local_boundary_prep",
            True,
            "Layer 11B current-user and ownership helpers prepare service boundaries but do not certify hosted tenant isolation.",
        ),
        billing_status=_capability(
            "not_implemented",
            False,
            "No billing provider, checkout, subscriptions, invoices, credit wallet, or paid plan controls exist.",
        ),
        export_delete_status=_capability(
            "not_implemented",
            False,
            "Account export and deletion controls are documented as future work only.",
        ),
        retention_status=_capability(
            "not_enforced",
            False,
            "Retention windows are documented as TBD and are not enforced in code.",
        ),
        durable_usage_metering_status=_capability(
            "not_implemented",
            False,
            "AI feature flags and a local session cap exist, but durable usage events, quotas, and ledgers remain future.",
        ),
        deployment_status=deployment_status,
        hosted_collaboration_status=_capability(
            "not_implemented",
            False,
            "Advisor packet preview/export is local-only; hosted collaboration, invitations, comments, and sharing remain future.",
        ),
        marketplace_employer_side_status=_capability(
            "not_implemented",
            False,
            "No employer, recruiter, marketplace, sponsored ranking, or public sharing capabilities exist.",
        ),
        known_blockers=known_blockers,
        production_readiness_statement=(
            "Careero is not production-ready unless production auth, tenant isolation, "
            "privacy lifecycle controls, durable usage metering, billing gates, "
            "deployment operations, and required workflow gates all pass."
        ),
    )
