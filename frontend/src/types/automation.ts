export type AutomationActionType =
  | "follow_up_suggestion"
  | "reminder_suggestion"
  | "artifact_readiness_check"
  | "communication_draft"
  | "workflow_state_suggestion"
  | "opportunity_review_suggestion"
  | "future_external_action_disabled";

export type AutomationTargetType =
  | "workspace"
  | "opportunity"
  | "application"
  | "artifact"
  | "reminder";

export type AutomationSuggestionStatus =
  | "active"
  | "dismissed"
  | "rejected"
  | "approved"
  | "expired";

export type AutomationApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "dismissed"
  | "expired";

export type AutomationExecutionStatus =
  | "not_applicable"
  | "pending"
  | "succeeded"
  | "failed"
  | "canceled";

export interface AutomationPreview {
  title: string;
  body: string;
  content_hash: string;
  external_mutation: false;
}

export interface AutomationSuggestion {
  id: string;
  workspace_id: string;
  target_type: AutomationTargetType | string;
  target_id: string;
  role_id: string | null;
  application_id: string | null;
  artifact_id: string | null;
  action_type: AutomationActionType | string;
  title: string;
  summary: string;
  reason: string;
  basis: string;
  confidence: string;
  source_inputs: Record<string, unknown>;
  preview: AutomationPreview;
  preview_hash: string;
  status: AutomationSuggestionStatus | string;
  expires_at: string | null;
  policy_version: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AutomationSuggestionListResponse {
  workspace_id: string | null;
  target_type: AutomationTargetType | string | null;
  target_id: string | null;
  suggestions: AutomationSuggestion[];
  external_actions_enabled: false;
}

export interface AutomationApprovalLog {
  id: string;
  workspace_id: string;
  suggestion_id: string;
  actor: string;
  target_type: AutomationTargetType | string;
  target_id: string;
  action_type: AutomationActionType | string;
  preview: AutomationPreview;
  preview_hash: string;
  approval_status: AutomationApprovalStatus | string;
  dismissal_or_rejection_reason: string | null;
  execution_status: AutomationExecutionStatus | string;
  execution_result: Record<string, unknown>;
  external_mutation: false;
  policy_version: string;
  created_at: string;
  decided_at: string | null;
  executed_at: string | null;
}

export interface AutomationApprovalLogListResponse {
  workspace_id: string | null;
  logs: AutomationApprovalLog[];
}

export interface AutomationPreferences {
  id: string;
  workspace_id: string;
  enabled: boolean;
  suggestion_categories: AutomationActionType[];
  follow_up_suggestion_days: number;
  artifact_readiness_checks_enabled: boolean;
  communication_drafts_enabled: boolean;
  internal_state_change_suggestions_enabled: boolean;
  future_external_actions_enabled: false;
  quiet_mode: boolean;
  policy_version: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AutomationPreferencesPayload {
  enabled?: boolean;
  suggestion_categories?: AutomationActionType[];
  follow_up_suggestion_days?: number;
  artifact_readiness_checks_enabled?: boolean;
  communication_drafts_enabled?: boolean;
  internal_state_change_suggestions_enabled?: boolean;
  future_external_actions_enabled?: false;
  quiet_mode?: boolean;
}
