import { apiRequest } from "./client";
import type { ArtifactPerformanceResponse } from "../types/artifactPerformance";

export function getArtifactPerformance(options?: {
  workspaceId?: string | null;
}): Promise<ArtifactPerformanceResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) {
    params.set("workspace_id", options.workspaceId);
  }
  const query = params.toString();
  return apiRequest<ArtifactPerformanceResponse>(
    `/api/analytics/artifacts${query ? `?${query}` : ""}`,
  );
}
