export type ResumeSourceType = "master_resume" | "profile" | "linkedin_export" | "other";

export interface ResumeSourceVersion {
  id: string;
  source_id: string;
  version_label: string;
  raw_text: string;
  normalized_summary: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResumeSource {
  id: string;
  name: string;
  source_type: ResumeSourceType | string;
  created_at: string;
  updated_at: string;
  latest_version: ResumeSourceVersion | null;
  active_version: ResumeSourceVersion | null;
}

export interface ActiveResumeSource {
  source: ResumeSource;
  version: ResumeSourceVersion;
}

export interface ResumeSourceCreatePayload {
  name: string;
  source_type: ResumeSourceType;
  version_label: string;
  raw_text: string;
  normalized_summary?: string | null;
  is_active: boolean;
}

export interface ResumeSourceVersionCreatePayload {
  version_label: string;
  raw_text: string;
  normalized_summary?: string | null;
  is_active: boolean;
}

export interface ResumeSourceImportResponse {
  file_name: string;
  file_type: string;
  content_type: string;
  size_bytes: number;
  character_count: number;
  warnings: string[];
  extracted_text: string;
}
