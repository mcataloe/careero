import { apiRequest } from "./client";
import type { Workspace } from "../types/workspaces";

export function listWorkspaces(options?: {
  includeInactive?: boolean;
}): Promise<Workspace[]> {
  const params = new URLSearchParams();
  if (options?.includeInactive) {
    params.set("include_inactive", "true");
  }
  const query = params.toString();
  return apiRequest<Workspace[]>(query ? `/api/workspaces?${query}` : "/api/workspaces");
}
