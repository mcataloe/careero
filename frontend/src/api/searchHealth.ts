import { apiRequest } from "./client";
import type { SearchHealthResponse } from "../types/searchHealth";

export function getSearchHealth(options?: {
  workspaceId?: string | null;
}): Promise<SearchHealthResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<SearchHealthResponse>(
    `/api/analytics/search-health${query ? `?${query}` : ""}`,
  );
}
