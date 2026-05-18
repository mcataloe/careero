export interface SearchHealthSignal {
  signal_type: string;
  label: string;
  message: string;
  gentle_guidance: string;
  basis: string;
  confidence: string;
  severity: string;
  source_inputs: Record<string, unknown>;
}

export interface SearchHealthResponse {
  workspace_id: string | null;
  signals: SearchHealthSignal[];
  insufficient_data: string[];
}
