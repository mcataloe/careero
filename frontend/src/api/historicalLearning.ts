import { apiRequest } from "./client";
import type { HistoricalLearningResponse } from "../types/historicalLearning";

export function getHistoricalLearning(options?: {
  workspaceId?: string | null;
}): Promise<HistoricalLearningResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<HistoricalLearningResponse>(
    `/api/analytics/history${query ? `?${query}` : ""}`,
  );
}
