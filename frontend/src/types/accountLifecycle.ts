export type AccountLifecycleRequestType =
  | "data_export"
  | "account_deletion"
  | "workspace_deletion"
  | "source_deletion"
  | "artifact_deletion"
  | "retention_review";

export interface AccountLifecycleRequest {
  id: string;
  user_id: string;
  request_type: AccountLifecycleRequestType;
  status: string;
  requested_at: string;
  acknowledged_at: string | null;
  completed_at: string | null;
  canceled_at: string | null;
  request_reason: string | null;
  target_type: string | null;
  target_id: string | null;
  request_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  message: string;
}

export interface AccountLifecycleRequestList {
  requests: AccountLifecycleRequest[];
  lifecycle_note: string;
}

export interface AccountLifecycleRequestCreate {
  request_type: AccountLifecycleRequestType;
  request_reason?: string;
  target_type?: string;
  target_id?: string;
  request_metadata?: Record<string, unknown>;
  deletion_confirmation?: string;
}
