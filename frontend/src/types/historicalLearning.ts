export interface HistoricalLearningSummary {
  label: string;
  value: string | number | null;
  basis: string;
  confidence: string;
  source_inputs: Record<string, unknown>;
}

export interface HistoricalLearningResponse {
  workspace_id: string | null;
  summaries: HistoricalLearningSummary[];
  insufficient_data: string[];
}
