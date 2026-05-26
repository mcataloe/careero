export interface AdvisorPacketWarning {
  code: string;
  message: string;
}

export interface AdvisorPacketRedaction {
  data_class: string;
  default_visibility: string;
  status: "included" | "excluded" | "summary_only";
  reason: string;
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
  updated_at: string;
  warnings: AdvisorPacketWarning[];
}

export interface AdvisorPacket {
  packet_version: string;
  mode: "local_preview";
  generated_at: string;
  local_only: boolean;
  external_sharing_enabled: boolean;
  advisory_notice: string;
  opportunity: AdvisorPacketOpportunitySummary;
  application: AdvisorPacketApplicationSummary;
  artifacts: AdvisorPacketArtifactSummary[];
  redactions: AdvisorPacketRedaction[];
  warnings: AdvisorPacketWarning[];
}
