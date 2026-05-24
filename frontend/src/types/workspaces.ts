export interface Workspace {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  workspace_type: string;
  status: string;
  preferences: Record<string, unknown>;
  ai_context_summary: string | null;
  tags: string[];
  metadata: Record<string, unknown>;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}
