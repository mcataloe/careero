import { apiRequest } from "./client";
import type {
  ApplicationDetail,
  ApplicationPipelineResponse,
  ApplicationStateTransitionPayload,
  ApplicationSummary,
  ApplicationTimelineEvent,
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

export function getApplication(applicationId: string): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(`/api/applications/${applicationId}`);
}

export function getApplicationTimeline(
  applicationId: string,
): Promise<ApplicationTimelineEvent[]> {
  return apiRequest<ApplicationTimelineEvent[]>(
    `/api/applications/${applicationId}/timeline`,
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
