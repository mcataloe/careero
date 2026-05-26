export type ReadinessStage =
  | "local_poc"
  | "local_beta_candidate"
  | "local_beta_blocked"
  | "private_beta_blocked"
  | "production_blocked";

export interface CapabilityReadiness {
  status: string;
  implemented: boolean;
  detail: string;
}

export interface LocalWorkflowReadiness {
  core_workflow: CapabilityReadiness;
  application_workflow: CapabilityReadiness;
  artifact_lifecycle: CapabilityReadiness;
  integrations: CapabilityReadiness;
  automation: CapabilityReadiness;
}

export interface AiFeatureFlags {
  role_parsing_enabled: boolean;
  compass_enrichment_enabled: boolean;
  resume_generation_enabled: boolean;
  cover_letter_generation_enabled: boolean;
  provider_key_configured: boolean;
  local_session_attempt_cap: number;
  durable_metering_status: string;
}

export interface ProductizationReadiness {
  environment: string;
  readiness_stage: ReadinessStage;
  production_ready: boolean;
  local_first_status: string;
  local_workflow_readiness: LocalWorkflowReadiness;
  database_health: string;
  ai_feature_flags: AiFeatureFlags;
  auth_status: CapabilityReadiness;
  tenant_boundary_prep_status: CapabilityReadiness;
  billing_status: CapabilityReadiness;
  export_delete_status: CapabilityReadiness;
  retention_status: CapabilityReadiness;
  durable_usage_metering_status: CapabilityReadiness;
  deployment_status: CapabilityReadiness;
  hosted_collaboration_status: CapabilityReadiness;
  marketplace_employer_side_status: CapabilityReadiness;
  known_blockers: string[];
  production_readiness_statement: string;
}
