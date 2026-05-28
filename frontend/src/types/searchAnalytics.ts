import type { Insight } from "./insights";

export interface AnalyticsMetric {
  value: number | null;
  label: string;
  basis: string;
}

export interface StageConversionMetric {
  from_stage: string;
  to_stage: string;
  numerator: number;
  denominator: number;
  rate: number | null;
  basis: string;
}

export interface StageDurationMetric {
  from_stage: string;
  to_stage: string;
  average_days: number | null;
  sample_size: number;
  basis: string;
}

export interface SegmentResponseMetric {
  segment: string;
  responses: number;
  total: number;
  response_rate: number | null;
  basis: string;
}

export interface SearchAnalyticsResponse {
  generated_at: string;
  workspace_id: string | null;
  scope: string;
  summary: Record<string, AnalyticsMetric>;
  conversion_rates: StageConversionMetric[];
  average_stage_durations: StageDurationMetric[];
  segment_response_rates: SegmentResponseMetric[];
  signals: Insight[];
  insufficient_data: string[];
}
