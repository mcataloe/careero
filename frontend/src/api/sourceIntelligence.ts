import { apiRequest } from "./client";
import type { SourceIntelligenceResponse } from "../types/sourceIntelligence";

export function getSourceIntelligence(options?: {
  workspaceId?: string | null;
}): Promise<SourceIntelligenceResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<SourceIntelligenceResponse>(
    `/api/analytics/sources${query ? `?${query}` : ""}`,
  );
}
