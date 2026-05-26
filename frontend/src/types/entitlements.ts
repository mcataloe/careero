export interface EntitlementItem {
  key: string;
  enabled: boolean;
  category: string;
  description: string;
}

export interface FeatureLimit {
  key: string;
  value: number | string | null;
  description: string;
}

export interface CurrentEntitlements {
  plan_id: string;
  plan_display_name: string;
  billing_status: "not_configured";
  payment_provider: "none";
  entitlements: EntitlementItem[];
  feature_limits: FeatureLimit[];
  unavailable_future_features: string[];
  monetization_guardrails: string[];
  local_first_note: string;
  metadata: Record<string, unknown>;
}
