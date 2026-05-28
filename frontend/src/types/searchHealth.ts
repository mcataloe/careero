import type { Insight } from "./insights";

export interface SearchHealthSignal extends Insight {
  signal_type: string;
  gentle_guidance: string;
}

export interface SearchHealthResponse {
  generated_at: string;
  workspace_id: string | null;
  signals: SearchHealthSignal[];
  insufficient_data: string[];
}
