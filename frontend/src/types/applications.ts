export type ApplicationWorkflowState =
  | "discovered"
  | "interested"
  | "applied"
  | "interviewing"
  | "offer"
  | "rejected"
  | "withdrawn"
  | "archived";

export interface ApplicationCompanySummary {
  id: string;
  name: string;
  website_url: string | null;
}

export interface ApplicationWorkflowCounts {
  notes: number;
  reminders: number;
  interviews: number;
}

export interface ApplicationSummary {
  id: string;
  role_id: string;
  workspace_id: string;
  title: string;
  company: ApplicationCompanySummary;
  current_state: ApplicationWorkflowState;
  applied_at: string | null;
  next_action_at: string | null;
  updated_at: string;
  archived_at: string | null;
  available_next_states: ApplicationWorkflowState[];
  counts: ApplicationWorkflowCounts;
}

export interface ApplicationPipelineResponse {
  workspace_id: string | null;
  include_inactive: boolean;
  states: Record<string, ApplicationSummary[]>;
}

export interface ApplicationStateTransitionPayload {
  state: ApplicationWorkflowState;
  reason?: string | null;
  changed_by?: "user" | "system" | "automation";
  metadata?: Record<string, unknown>;
  reactivate?: boolean;
}
