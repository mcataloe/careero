export interface AdvisorPacketWarning {
  code: string;
  message: string;
}

export interface AdvisorPacketIncludeOptions {
  artifact_ids: string[];
  external_link_ids: string[];
  interview_stage_ids: string[];
  reminder_ids: string[];
  advisor_context: string | null;
}

export interface AdvisorPacketRedaction {
  data_class: string;
  field: string | null;
  default_visibility: string;
  status: "included" | "excluded" | "summary_only";
  included: boolean;
  reason: string;
  warning: string | null;
}

export interface AdvisorPacketSection {
  key: string;
  title: string;
  status: "included" | "excluded" | "summary_only";
  item_count: number;
  warnings: AdvisorPacketWarning[];
}

export interface AdvisorPacketOpportunitySummary {
  id: string;
  workspace_id: string;
  title: string;
  company_name: string;
  status: string;
  location: string | null;
  remote_type: string | null;
}

export interface AdvisorPacketApplicationSummary {
  id: string;
  current_state: string;
  applied_at: string | null;
  next_action_at: string | null;
  counts: Record<string, number>;
}

export interface AdvisorPacketArtifactSummary {
  id: string;
  artifact_type: string;
  title: string;
  lifecycle_status: string | null;
  revision_number: number | null;
  content_included: boolean;
  content: string | null;
  updated_at: string;
  warnings: AdvisorPacketWarning[];
}

export interface AdvisorPacketExternalLinkSummary {
  id: string;
  label: string;
  url: string;
  link_type: string | null;
  warning: string;
}

export interface AdvisorPacketInterviewSummary {
  id: string;
  title: string;
  stage_type: string;
  status: string;
  scheduled_at: string | null;
  completed_at: string | null;
  notes_included: boolean;
  notes: string | null;
  preparation_notes: string | null;
  outcome_notes: string | null;
  warning: string;
}

export interface AdvisorPacketReminderSummary {
  id: string;
  title: string;
  due_at: string;
  completed_at: string | null;
  notes_included: boolean;
  notes: string | null;
  warning: string;
}

export interface AdvisorPacket {
  packet_version: string;
  mode: "local_preview";
  generated_at: string;
  local_only: boolean;
  external_sharing_enabled: boolean;
  advisory_notice: string;
  include_options: AdvisorPacketIncludeOptions;
  sections: AdvisorPacketSection[];
  opportunity: AdvisorPacketOpportunitySummary;
  application: AdvisorPacketApplicationSummary;
  artifacts: AdvisorPacketArtifactSummary[];
  selected_external_links: AdvisorPacketExternalLinkSummary[];
  selected_interviews: AdvisorPacketInterviewSummary[];
  selected_reminders: AdvisorPacketReminderSummary[];
  advisor_context: string | null;
  redactions: AdvisorPacketRedaction[];
  warnings: AdvisorPacketWarning[];
}

export interface AdvisorPacketPreviewOptions {
  artifactIds?: string[];
  externalLinkIds?: string[];
  interviewStageIds?: string[];
  reminderIds?: string[];
  advisorContext?: string;
}
