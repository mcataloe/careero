import type { Insight } from "./insights";

export interface Recommendation extends Insight {
  recommendation_type: string;
  subject_type: string;
  subject_id: string | null;
  action: string;
  title: string;
  reason: string;
}

export interface RecommendationListResponse {
  generated_at: string;
  workspace_id: string | null;
  recommendations: Recommendation[];
  read_only: boolean;
}
