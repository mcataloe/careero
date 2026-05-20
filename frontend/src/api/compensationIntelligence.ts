import { apiRequest } from "./client";
import type { CompensationIntelligenceResponse } from "../types/compensationIntelligence";

export function getCompensationIntelligence(options?: {
  workspaceId?: string | null;
}): Promise<CompensationIntelligenceResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<CompensationIntelligenceResponse>(
    `/api/analytics/compensation${query ? `?${query}` : ""}`,
  );
}
