export type RoleStatus = "found" | "interested" | "applied" | "archived";

export type SourceType =
  | "manual"
  | "linkedin_manual"
  | "linkedin"
  | "recruiter"
  | "recruiter_email"
  | "referral"
  | "company_site"
  | "job_board"
  | "networking"
  | "direct_outreach"
  | "internal_referral"
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
  parse_metadata: RoleParseMetadata;
  status: RoleStatus;
  date_found: string;
  date_posted: string | null;
  created_at: string;
  updated_at: string;
  company: Company;
  source: JobSource | null;
}

export interface RoleParseMetadata {
  parserVersion?: string;
  aiModel?: string;
  parseTimestamp?: string;
  parseWarnings?: string[];
  confidence?: Record<string, number>;
  userEditedFields?: string[];
  extractedSkills?: string[];
  opportunityIntelligence?: OpportunityIntelligence;
  [key: string]: unknown;
}

export interface OpportunitySignal {
  type: string;
  label: string;
  severity: "low" | "medium" | "high" | string;
  reason: string;
  basis: string;
  confidence: string;
  evidence: unknown[];
}

export interface OpportunityIntelligence {
  version: string;
  evaluatedAt: string;
  signals: OpportunitySignal[];
  categories: string[];
  summary: string;
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
  parse_metadata?: RoleParseMetadata;
  status: RoleStatus;
  date_found?: string | null;
  date_posted?: string | null;
}

export interface RoleParseRequest {
  rawText: string;
  source?: SourceType | null;
  jobUrl?: string | null;
}

export interface ParsedRole {
  roleTitle?: string | null;
  company?: string | null;
  companyWebsite?: string | null;
  jobUrl?: string | null;
  source?: SourceType | null;
  location?: string | null;
  remoteType?: string | null;
  compensationMin?: number | string | null;
  compensationMax?: number | string | null;
  currency?: string | null;
  employmentType?: string | null;
  seniority?: string | null;
  datePosted?: string | null;
  normalizedDescription?: string | null;
  extractedSkills?: string[];
  warnings?: string[];
  confidence?: Record<string, number>;
}

export interface RoleParseResponse {
  parsed: ParsedRole;
  metadata: {
    parserVersion: string;
    model: string;
  };
}

export interface RoleUpdatePayload {
  title?: string;
  status?: RoleStatus;
  remote_type?: string | null;
  normalized_description?: string | null;
}

export type Opportunity = Role;
export type OpportunityCreatePayload = RoleCreatePayload;
export type OpportunityUpdatePayload = RoleUpdatePayload;
export type OpportunityParseRequest = RoleParseRequest;
export type OpportunityParseResponse = RoleParseResponse;
