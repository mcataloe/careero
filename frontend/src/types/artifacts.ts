export type ArtifactLifecycleStatus =
  | "draft"
  | "reviewed"
  | "submitted"
  | "archived";

export type ArtifactType = "tailored_resume" | "cover_letter";

export interface ArtifactTraceability {
  workspace_id: string;
  role_id: string | null;
  opportunity_id: string | null;
  application_id: string | null;
  evaluation_id: string | null;
  source_resume_version_id: string | null;
  source_artifact_id: string | null;
  parent_artifact_id: string | null;
  generation_warnings: string[];
  export_formats: string[];
}

export interface ArtifactRecord {
  id: string;
  workspace_id: string;
  application_id: string | null;
  role_id: string | null;
  opportunity_id: string | null;
  artifact_type: ArtifactType | string;
  lifecycle_status: ArtifactLifecycleStatus;
  version_number: number;
  title: string;
  content: string;
  reviewed_at: string | null;
  submitted_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  traceability: ArtifactTraceability;
  available_transitions: ArtifactLifecycleStatus[];
  new_version_created: boolean;
  source_submitted_artifact_id: string | null;
  metadata: {
    revision_id?: string | null;
    change_summary?: string | null;
  };
}

export interface ArtifactDraftUpdatePayload {
  title?: string;
  content?: string;
  change_summary?: string | null;
}
