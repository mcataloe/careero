import { apiRequest } from "./client";
import type {
  ApplicationPipelineResponse,
  ApplicationStateTransitionPayload,
  ApplicationSummary,
} from "../types/applications";

function appendPipelineParams(
  path: string,
  {
    workspaceId,
    includeInactive,
  }: {
    workspaceId?: string | null;
    includeInactive?: boolean;
  } = {},
) {
  const params = new URLSearchParams();
  if (workspaceId) {
    params.set("workspace_id", workspaceId);
  }
  if (includeInactive) {
    params.set("include_inactive", "true");
  }
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

export function getApplicationsPipeline(options?: {
  workspaceId?: string | null;
  includeInactive?: boolean;
}): Promise<ApplicationPipelineResponse> {
  return apiRequest<ApplicationPipelineResponse>(
    appendPipelineParams("/api/applications/pipeline", options),
  );
}

export function getWorkspaceApplicationsPipeline(
  workspaceId: string,
  options?: { includeInactive?: boolean },
): Promise<ApplicationPipelineResponse> {
  return apiRequest<ApplicationPipelineResponse>(
    appendPipelineParams(`/api/workspaces/${workspaceId}/applications/pipeline`, {
      includeInactive: options?.includeInactive,
    }),
  );
}

export function transitionApplicationState(
  applicationId: string,
  payload: ApplicationStateTransitionPayload,
): Promise<ApplicationSummary> {
  return apiRequest<ApplicationSummary>(
    `/api/applications/${applicationId}/state-transitions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}
