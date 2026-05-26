import { apiRequest } from "./client";
import type { CompassInsightsResponse } from "../types/compassInsights";

export function getCompassInsights(options?: {
  workspaceId?: string | null;
}): Promise<CompassInsightsResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<CompassInsightsResponse>(
    `/api/analytics/compass${query ? `?${query}` : ""}`,
  );
}
