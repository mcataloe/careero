export interface LocalDataExport {
  metadata: {
    schema_version: string;
    generated_at: string;
    readiness_note: string;
    current_user: {
      id: string;
      email: string;
      display_name: string;
      mode: string;
      environment: string;
    };
    derived_data_notes: string[];
  };
  workspaces: Record<string, unknown>[];
  companies: Record<string, unknown>[];
  job_sources: Record<string, unknown>[];
  opportunities: Record<string, unknown>[];
  resume_sources: Record<string, unknown>[];
  resume_source_versions: Record<string, unknown>[];
  compass_evaluations: Record<string, unknown>[];
  generated_artifacts: Record<string, unknown>[];
  artifact_performance_records: Record<string, unknown>[];
  applications: Record<string, unknown>[];
  application_state_history: Record<string, unknown>[];
  notes: Record<string, unknown>[];
  reminders: Record<string, unknown>[];
  external_links: Record<string, unknown>[];
  interview_stages: Record<string, unknown>[];
  activity_logs: Record<string, unknown>[];
  account_lifecycle_requests: Record<string, unknown>[];
  ai_usage_events: Record<string, unknown>[];
  automation_suggestions: Record<string, unknown>[];
  automation_approval_logs: Record<string, unknown>[];
}
