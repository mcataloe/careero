export interface CompassTrendInsight {
  label: string;
  message: string;
  basis: string;
  confidence: string;
  severity: string;
  source_inputs: Record<string, unknown>;
}

export interface CompassInsightsResponse {
  workspace_id: string | null;
  average_compass_score: number | null;
  insights: CompassTrendInsight[];
  insufficient_data: string[];
}
