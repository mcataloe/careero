export interface ArtifactPerformanceMetric {
  label: string;
  artifact_type: string | null;
  variant_name: string | null;
  role_category: string | null;
  total: number;
  responses: number;
  interviews: number;
  response_rate: number | null;
  interview_rate: number | null;
  basis: string;
}

export interface ArtifactPerformanceResponse {
  workspace_id: string | null;
  summary: ArtifactPerformanceMetric[];
  by_variant: ArtifactPerformanceMetric[];
  by_role_category: ArtifactPerformanceMetric[];
  insights: Array<Record<string, unknown>>;
  insufficient_data: string[];
}
