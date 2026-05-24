import { apiRequest } from "./client";
import type {
  CareerStrategySummary,
  SearchTrackStrategySummary,
} from "../types/strategy";

export function getWorkspaceStrategy(
  workspaceId: string,
): Promise<SearchTrackStrategySummary> {
  return apiRequest<SearchTrackStrategySummary>(
    `/api/strategy/workspaces/${workspaceId}`,
  );
}

export function getCareerStrategy(options?: {
  includeCrossTrack?: boolean;
}): Promise<CareerStrategySummary> {
  const params = new URLSearchParams();
  if (options?.includeCrossTrack) {
    params.set("include_cross_track", "true");
  }
  const query = params.toString();
  return apiRequest<CareerStrategySummary>(
    `/api/strategy/workspaces${query ? `?${query}` : ""}`,
  );
}
