import { apiRequest } from "./client";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";

export function getSearchAnalytics(options?: {
  workspaceId?: string | null;
}): Promise<SearchAnalyticsResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<SearchAnalyticsResponse>(
    `/api/analytics/search${query ? `?${query}` : ""}`,
  );
}
