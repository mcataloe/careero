import type { Insight } from "./insights";

export interface HistoricalLearningSummary extends Insight {
  value: string | number | null;
}

export interface HistoricalLearningResponse {
  generated_at: string;
  workspace_id: string | null;
  summaries: HistoricalLearningSummary[];
  insufficient_data: string[];
}
