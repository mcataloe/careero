import type { Insight } from "./insights";

export interface CompensationObservation {
  role_id: string;
  title: string;
  compensation_min: number | null;
  compensation_max: number | null;
  midpoint: number | null;
  currency: string | null;
  employment_type: string | null;
  remote_type: string | null;
  source_basis: string;
}

export type CompensationInsight = Insight;

export interface CompensationIntelligenceResponse {
  generated_at: string;
  workspace_id: string | null;
  target_compensation_min: number | null;
  observations: CompensationObservation[];
  insights: CompensationInsight[];
  insufficient_data: string[];
}
