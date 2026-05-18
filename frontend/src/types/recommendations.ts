export interface Recommendation {
  id: string;
  recommendation_type: string;
  subject_type: string;
  subject_id: string | null;
  action: string;
  title: string;
  reason: string;
  basis: string;
  confidence: string;
  source_inputs: Record<string, unknown>;
}

export interface RecommendationListResponse {
  workspace_id: string | null;
  recommendations: Recommendation[];
  read_only: boolean;
}
