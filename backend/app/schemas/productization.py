from typing import Literal

from pydantic import BaseModel, ConfigDict


ReadinessStage = Literal[
    "local_poc",
    "local_beta_candidate",
    "local_beta_blocked",
    "private_beta_blocked",
    "production_blocked",
]


class CapabilityReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    implemented: bool
    detail: str


class LocalWorkflowReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    core_workflow: CapabilityReadiness
    application_workflow: CapabilityReadiness
    artifact_lifecycle: CapabilityReadiness
    integrations: CapabilityReadiness
    automation: CapabilityReadiness


class AiFeatureFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_parsing_enabled: bool
    compass_enrichment_enabled: bool
    resume_generation_enabled: bool
    cover_letter_generation_enabled: bool
    provider_key_configured: bool
    local_session_attempt_cap: int
    durable_metering_status: str


class ProductizationReadinessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    environment: str
    readiness_stage: ReadinessStage
    production_ready: bool
    local_first_status: str
    local_workflow_readiness: LocalWorkflowReadiness
    database_health: str
    ai_feature_flags: AiFeatureFlags
    auth_status: CapabilityReadiness
    tenant_boundary_prep_status: CapabilityReadiness
    billing_status: CapabilityReadiness
    export_delete_status: CapabilityReadiness
    retention_status: CapabilityReadiness
    durable_usage_metering_status: CapabilityReadiness
    deployment_status: CapabilityReadiness
    hosted_collaboration_status: CapabilityReadiness
    marketplace_employer_side_status: CapabilityReadiness
    known_blockers: list[str]
    production_readiness_statement: str
