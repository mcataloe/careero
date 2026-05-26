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
  workspace_id: string | null;
  summaries: SourceSummaryMetric[];
  insights: Array<Record<string, unknown>>;
  insufficient_data: string[];
}
