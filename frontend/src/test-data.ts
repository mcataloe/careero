import type { Role } from "./types/roles";
import type { StrideEvaluation } from "./types/strideEvaluations";

export const sampleRole: Role = {
  id: "11111111-1111-4111-8111-111111111111",
  title: "Senior Backend Engineer",
  company_id: "22222222-2222-4222-8222-222222222222",
  source_id: "33333333-3333-4333-8333-333333333333",
  job_url: "https://www.linkedin.com/jobs/view/example",
  location: "Chicago, IL",
  remote_type: "hybrid",
  compensation_min: "120000.00",
  compensation_max: "150000.00",
  compensation_currency: "USD",
  raw_description: "Raw pasted job description",
  normalized_description: "Normalized job description",
  status: "found",
  date_found: "2026-05-13",
  date_posted: "2026-05-01",
  created_at: "2026-05-13T12:00:00Z",
  updated_at: "2026-05-13T12:00:00Z",
  company: {
    id: "22222222-2222-4222-8222-222222222222",
    name: "Example Company",
    website_url: "https://example.com",
  },
  source: {
    id: "33333333-3333-4333-8333-333333333333",
    name: "LinkedIn manual",
    source_type: "linkedin_manual",
  },
};

export const sampleEvaluation: StrideEvaluation = {
  id: "44444444-4444-4444-8444-444444444444",
  user_id: "00000000-0000-4000-8000-000000000001",
  role_id: sampleRole.id,
  evaluation_status: "completed",
  overall_score: "82.00",
  recommendation: "apply",
  confidence_level: "medium",
  summary: "Strong baseline fit for backend platform work.",
  strengths: [
    {
      code: "technical_match",
      message: "Python and PostgreSQL are explicit role signals.",
      evidence: "Python and PostgreSQL platforms",
      status: "strong_match",
    },
  ],
  concerns: [
    {
      code: "missing_resume_evidence",
      message: "Kubernetes evidence is not present in the active profile.",
      severity: "medium",
    },
  ],
  resume_alignment: {
    status: "partial_match",
    score: 72,
    notes: "Profile supports backend platform work.",
    evidence: ["Python services"],
  },
  compensation_alignment: {
    status: "grounded",
    score: 80,
    notes: "Compensation is in range.",
  },
  seniority_alignment: {
    status: "strong_match",
    score: 85,
    notes: "Senior scope is supported.",
  },
  remote_alignment: {
    status: "partial_match",
    score: 70,
    notes: "Hybrid role may need review.",
  },
  technical_alignment: {
    status: "strong_match",
    score: 88,
    notes: "Python and PostgreSQL match.",
  },
  company_risk: {
    status: "insufficient_data",
    score: null,
    notes: "No external company research is used.",
  },
  ats_keywords: ["python", "postgresql"],
  missing_keywords: ["kubernetes"],
  raw_evaluation_json: {
    ai_status: "skipped",
    ai_failure_reason: "AI evaluations are disabled",
    ai_result: {
      unsupported_claim_warnings: [
        {
          code: "no_kubernetes_evidence",
          message: "Do not claim Kubernetes experience without source evidence.",
          status: "no_evidence",
        },
      ],
    },
  },
  created_at: "2026-05-13T12:00:00Z",
  updated_at: "2026-05-13T12:00:00Z",
};
