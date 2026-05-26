export interface AIUsageEvent {
  id: string;
  user_id: string;
  workspace_id: string | null;
  role_id: string | null;
  application_id: string | null;
  artifact_id: string | null;
  feature: string;
  event_type: string;
  provider: string | null;
  model: string | null;
  status: string;
  prompt_version: string | null;
  ruleset_version: string | null;
  input_token_estimate: number | null;
  output_token_estimate: number | null;
  latency_ms: number | null;
  error_class: string | null;
  content_hash: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AIUsageSummary {
  total_events: number;
  by_feature: Record<string, number>;
  by_event_type: Record<string, number>;
}

export interface AIUsageList {
  events: AIUsageEvent[];
  summary: AIUsageSummary;
  usage_note: string;
}
