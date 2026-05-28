export type InsightCategory =
  | "fit_alignment"
  | "risk_red_flag"
  | "compensation"
  | "remote_location_alignment"
  | "seniority_alignment"
  | "application_workflow"
  | "artifact_readiness"
  | "follow_up_action"
  | "cross_opportunity_comparison"
  | "search_track_strategy"
  | "compass"
  | "source_intelligence"
  | "historical_learning"
  | "other"
  | "unknown";

export type InsightGenerationMethod =
  | "ai_generated"
  | "deterministic"
  | "user_authored"
  | "imported"
  | "hybrid"
  | "unknown";

export type InsightConfidenceLevel =
  | "insufficient_data"
  | "weak"
  | "moderate"
  | "high"
  | "unknown";

export type InsightSeverity =
  | "info"
  | "positive"
  | "caution"
  | "warning"
  | "critical";

export type InsightVisibility = "internal" | "advisor_visible" | "user_exportable";

export interface InsightScope {
  user_scoped: boolean;
  workspace_id: string | null;
  opportunity_id: string | null;
  compass_evaluation_id: string | null;
  artifact_id: string | null;
  application_id: string | null;
}

export interface InsightSourceReference {
  source_type:
    | "opportunity"
    | "raw_job_description"
    | "parsed_fields"
    | "compass_evaluation"
    | "resume_source"
    | "artifact"
    | "user_note"
    | "application_event"
    | "workspace"
    | "other";
  source_id: string | null;
  label: string;
  field: string | null;
  metadata: Record<string, unknown>;
}

export interface InsightFreshness {
  generated_at: string;
  source_updated_at: string | null;
  is_stale: boolean;
  refresh_reason: string | null;
}

export interface InsightRecommendedAction {
  action_type: string;
  label: string;
  route_path: string | null;
  review_required: boolean;
  metadata: Record<string, unknown>;
}

export interface Insight {
  id: string;
  category: InsightCategory;
  label: string;
  message: string;
  basis: string;
  confidence: string;
  confidence_level: InsightConfidenceLevel;
  confidence_explanation: string | null;
  known_uncertainty: string[];
  warnings: string[];
  severity: InsightSeverity;
  priority: number | null;
  generation_method: InsightGenerationMethod;
  visibility: InsightVisibility;
  scope: InsightScope;
  source_references: InsightSourceReference[];
  source_inputs: Record<string, unknown>;
  freshness: InsightFreshness;
  recommended_action: InsightRecommendedAction | null;
  created_at: string | null;
  updated_at: string | null;
}
