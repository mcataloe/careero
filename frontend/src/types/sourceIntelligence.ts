import type { Insight } from "./insights";

export interface SourceSummaryMetric {
  source_type: string;
  label: string;
  opportunities: number;
  applications: number;
  responses: number;
  interviews: number;
  response_rate: number | null;
  interview_rate: number | null;
  average_compass_score: number | null;
  recruiter_contacts: number;
  compensation_aligned: number;
  basis: string;
}

export interface SourceIntelligenceResponse {
  generated_at: string;
  workspace_id: string | null;
  summaries: SourceSummaryMetric[];
  insights: Insight[];
  insufficient_data: string[];
}
