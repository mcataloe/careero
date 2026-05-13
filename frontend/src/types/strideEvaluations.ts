export type EvaluationStatus = "pending" | "completed" | "failed";
export type Recommendation = "apply" | "monitor" | "skip" | "needs_review";
export type ConfidenceLevel = "low" | "medium" | "high";

export interface EvaluationSection {
  status?: string;
  score?: number | string | null;
  notes?: string | null;
  evidence?: string[];
  matched_keywords?: string[];
  missing_keywords?: string[];
  [key: string]: unknown;
}

export interface EvidenceItem {
  code?: string;
  message?: string;
  evidence?: string | null;
  status?: string;
  dimension?: string;
  severity?: string;
  score?: number;
  keywords?: string[];
}

export interface StrideEvaluation {
  id: string;
  user_id: string;
  role_id: string;
  evaluation_status: EvaluationStatus;
  overall_score: string | null;
  recommendation: Recommendation | string | null;
  confidence_level: ConfidenceLevel | string | null;
  summary: string | null;
  strengths: EvidenceItem[];
  concerns: EvidenceItem[];
  resume_alignment: EvaluationSection;
  compensation_alignment: EvaluationSection;
  seniority_alignment: EvaluationSection;
  remote_alignment: EvaluationSection;
  technical_alignment: EvaluationSection;
  company_risk: EvaluationSection;
  ats_keywords: string[];
  missing_keywords: string[];
  raw_evaluation_json: {
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

export interface StrideEvaluationCreatePayload {
  user_notes?: string | null;
  user_context?: Record<string, unknown>;
}

export type EvaluationSummaryState =
  | { status: "loading" }
  | { status: "not_evaluated" }
  | { status: "error"; message: string }
  | { status: "completed"; evaluation: StrideEvaluation };
