export interface StrideTrendInsight {
  label: string;
  message: string;
  basis: string;
  confidence: string;
  severity: string;
  source_inputs: Record<string, unknown>;
}

export interface StrideInsightsResponse {
  workspace_id: string | null;
  average_stride_score: number | null;
  insights: StrideTrendInsight[];
  insufficient_data: string[];
}
