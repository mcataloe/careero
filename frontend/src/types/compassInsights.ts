import type { Insight } from "./insights";

export type CompassTrendInsight = Insight;

export interface CompassInsightsResponse {
  generated_at: string;
  workspace_id: string | null;
  average_compass_score: number | null;
  insights: CompassTrendInsight[];
  insufficient_data: string[];
}
