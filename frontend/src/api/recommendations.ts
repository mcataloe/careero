import { apiRequest } from "./client";
import type { RecommendationListResponse } from "../types/recommendations";

export function getRecommendations(options?: {
  workspaceId?: string | null;
}): Promise<RecommendationListResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<RecommendationListResponse>(
    `/api/recommendations${query ? `?${query}` : ""}`,
  );
}
