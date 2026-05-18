import { apiRequest } from "./client";
import type { StrideInsightsResponse } from "../types/strideInsights";

export function getStrideInsights(options?: {
  workspaceId?: string | null;
}): Promise<StrideInsightsResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<StrideInsightsResponse>(
    `/api/analytics/stride${query ? `?${query}` : ""}`,
  );
}
