export type RoleStatus = "found" | "interested" | "applied" | "archived";

export type SourceType =
  | "manual"
  | "linkedin_manual"
  | "greenhouse"
  | "lever"
  | "ashby"
  | "workable"
  | "other";

export interface Company {
  id: string;
  name: string;
  website_url: string | null;
}

export interface JobSource {
  id: string;
  name: string;
  source_type: string | null;
}

export interface Role {
  id: string;
  title: string;
  company_id: string;
  source_id: string | null;
  job_url: string | null;
  location: string | null;
  remote_type: string | null;
  compensation_min: string | null;
  compensation_max: string | null;
  compensation_currency: string | null;
  raw_description: string | null;
  normalized_description: string | null;
  status: RoleStatus;
  date_found: string;
  date_posted: string | null;
  created_at: string;
  updated_at: string;
  company: Company;
  source: JobSource | null;
}

export interface RoleCreatePayload {
  title: string;
  company: {
    name: string;
    website_url?: string | null;
  };
  source: {
    source_type: SourceType;
  };
  job_url?: string | null;
  location?: string | null;
  remote_type?: string | null;
  compensation_min?: string | null;
  compensation_max?: string | null;
  compensation_currency?: string | null;
  raw_description?: string | null;
  normalized_description?: string | null;
  status: RoleStatus;
  date_found?: string | null;
  date_posted?: string | null;
}

export interface RoleUpdatePayload {
  title?: string;
  status?: RoleStatus;
  remote_type?: string | null;
  normalized_description?: string | null;
}
