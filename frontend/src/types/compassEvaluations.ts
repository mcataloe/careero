export type EvaluationStatus = "pending" | "completed" | "failed";
export type Recommendation = "apply" | "monitor" | "skip" | "needs_review";
export type ConfidenceLevel = "low" | "medium" | "high";

export interface EvaluationSection {
  status?: string;
  score?: number | string | null;
  summary?: string | null;
  notes?: string | null;
  evidence?: string[];
  gaps?: string[];
  assumptions?: string[];
  matched_keywords?: string[];
  missing_keywords?: string[];
  [key: string]: unknown;
}

export interface EvidenceItem {
  label?: string;
  code?: string;
  message?: string;
  notes?: string | null;
  evidence?: string | string[] | null;
  status?: string;
  dimension?: string;
  severity?: string;
  score?: number;
  keywords?: string[];
}

export interface CompassEvaluation {
  id: string;
  user_id?: string;
  role_id?: string;
  workspaceId?: string;
  opportunityId?: string;
  evaluation_status?: EvaluationStatus;
  status?: EvaluationStatus | "superseded";
  overall_score?: string | null;
  overallScore?: number | null;
  recommendation?: Recommendation | string | null;
  recommendations?: {
    decision?: Recommendation | string | null;
    rationale?: string | null;
    nextActions?: string[];
  } | null;
  confidence_level?: ConfidenceLevel | string | null;
  confidence?: {
    level?: ConfidenceLevel | string | null;
    score?: number | null;
    rationale?: string | null;
  };
  summary: string | null;
  strengths: EvidenceItem[];
  gaps?: EvidenceItem[];
  risks?: EvidenceItem[];
  concerns?: EvidenceItem[];
  resume_alignment?: EvaluationSection;
  compensation_alignment?: EvaluationSection;
  seniority_alignment?: EvaluationSection;
  remote_alignment?: EvaluationSection;
  technical_alignment?: EvaluationSection;
  company_risk?: EvaluationSection;
  compensationFindings?: EvaluationSection & {
    notes?: string | null;
    evidence?: string[];
  };
  atsFindings?: {
    matchedKeywords?: string[];
    missingKeywords?: string[];
    keywordNotes?: string | null;
    score?: number | null;
  };
  sections?: {
    strategicFit?: EvaluationSection;
    technicalAlignment?: EvaluationSection;
    seniorityAlignment?: EvaluationSection;
    compensationAlignment?: EvaluationSection;
    remoteAlignment?: EvaluationSection;
    companyRisk?: EvaluationSection;
    applicationEffort?: EvaluationSection;
    atsResumeAlignment?: EvaluationSection;
  };
  assumptions?: string[];
  ats_keywords?: string[];
  missing_keywords?: string[];
  model_used: string | null;
  prompt_version: string | null;
  ruleset_version: string | null;
  input_token_estimate: number | null;
  output_token_estimate: number | null;
  latency_ms: number | null;
  ai_enabled: boolean;
  ai_status: "completed" | "failed" | "skipped" | string | null;
  error_message: string | null;
  role_content_hash: string | null;
  source_hash: string | null;
  evaluation_input_hash: string | null;
  raw_evaluation_json?: {
    ai_status?: "completed" | "failed" | "skipped";
    ai_failure_reason?: string;
    ai_error_type?: string;
    ai_result?: {
      unsupported_claim_warnings?: EvidenceItem[];
      evidence_matches?: EvidenceItem[];
      evidence_gaps?: EvidenceItem[];
      positioning_opportunities?: EvidenceItem[];
      [key: string]: unknown;
    };
    validationIssues?: unknown[];
    active_resume_source?: {
      source_id: string;
      source_name: string;
      source_type: string;
      version_id: string;
      version_label: string;
    } | null;
    [key: string]: unknown;
  };
  created_at: string;
  updated_at: string;
}

export interface CompassEvaluationCreatePayload {
  user_notes?: string | null;
  user_context?: Record<string, unknown>;
  force?: boolean;
}

export type EvaluationSummaryState =
  | { status: "loading" }
  | { status: "not_evaluated" }
  | { status: "error"; message: string }
  | { status: "completed"; evaluation: CompassEvaluation };
