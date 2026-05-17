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
  external_links: number;
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

export interface ApplicationRoleSummary {
  id: string;
  workspace_id: string;
  title: string;
  status: string;
  company: ApplicationCompanySummary;
  job_url: string | null;
  location: string | null;
  remote_type: string | null;
}

export interface ApplicationDetail extends ApplicationSummary {
  workflow_metadata: Record<string, unknown>;
  application_state: Record<string, unknown>;
  state_history: Record<string, unknown>[];
  role: ApplicationRoleSummary;
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

export interface ApplicationTimelineEvent {
  id: string;
  application_id: string;
  event_type: string;
  title: string;
  description: string | null;
  occurred_at: string;
  actor: string;
  source_type: string;
  source_id: string;
  metadata: Record<string, unknown>;
}

export type ApplicationNoteType =
  | "general"
  | "recruiter"
  | "compensation"
  | "follow_up"
  | "interview";

export interface ApplicationNote {
  id: string;
  application_id: string;
  workspace_id: string;
  author: string | null;
  note_type: ApplicationNoteType;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface ApplicationNotePayload {
  body: string;
  author?: string | null;
  note_type?: ApplicationNoteType;
}

export type ApplicationExternalLinkType =
  | "job_posting"
  | "company_careers"
  | "recruiter_profile"
  | "application_portal"
  | "interview_prep"
  | "email_thread"
  | "other";

export interface ApplicationExternalLink {
  id: string;
  application_id: string;
  workspace_id: string;
  label: string;
  url: string;
  type: ApplicationExternalLinkType | string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ApplicationExternalLinkPayload {
  label: string;
  url: string;
  type?: ApplicationExternalLinkType | string | null;
  metadata?: Record<string, unknown>;
}

export type ApplicationReminderType =
  | "follow_up"
  | "deadline"
  | "next_action"
  | "interview_prep"
  | "thank_you"
  | "status_check"
  | "revisit"
  | "submit_application"
  | "other";

export type ApplicationReminderPriority = "low" | "normal" | "high";

export interface ApplicationReminder {
  id: string;
  application_id: string;
  workspace_id: string;
  title: string;
  notes: string | null;
  due_at: string;
  completed_at: string | null;
  reminder_type: ApplicationReminderType | string;
  priority: ApplicationReminderPriority | string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceReminder extends ApplicationReminder {
  application_title: string;
  company_name: string;
}

export interface ApplicationReminderPayload {
  title: string;
  notes?: string | null;
  due_at: string;
  reminder_type?: ApplicationReminderType | string;
  priority?: ApplicationReminderPriority | string;
  metadata?: Record<string, unknown>;
}
