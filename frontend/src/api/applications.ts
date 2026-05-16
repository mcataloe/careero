import { apiRequest } from "./client";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationExternalLinkPayload,
  ApplicationNote,
  ApplicationNotePayload,
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

export function listApplicationNotes(
  applicationId: string,
): Promise<ApplicationNote[]> {
  return apiRequest<ApplicationNote[]>(`/api/applications/${applicationId}/notes`);
}

export function createApplicationNote(
  applicationId: string,
  payload: ApplicationNotePayload,
): Promise<ApplicationNote> {
  return apiRequest<ApplicationNote>(`/api/applications/${applicationId}/notes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateApplicationNote(
  applicationId: string,
  noteId: string,
  payload: Partial<ApplicationNotePayload>,
): Promise<ApplicationNote> {
  return apiRequest<ApplicationNote>(
    `/api/applications/${applicationId}/notes/${noteId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteApplicationNote(
  applicationId: string,
  noteId: string,
): Promise<void> {
  return apiRequest<void>(`/api/applications/${applicationId}/notes/${noteId}`, {
    method: "DELETE",
  });
}

export function listApplicationLinks(
  applicationId: string,
): Promise<ApplicationExternalLink[]> {
  return apiRequest<ApplicationExternalLink[]>(
    `/api/applications/${applicationId}/links`,
  );
}

export function createApplicationLink(
  applicationId: string,
  payload: ApplicationExternalLinkPayload,
): Promise<ApplicationExternalLink> {
  return apiRequest<ApplicationExternalLink>(
    `/api/applications/${applicationId}/links`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateApplicationLink(
  applicationId: string,
  linkId: string,
  payload: Partial<ApplicationExternalLinkPayload>,
): Promise<ApplicationExternalLink> {
  return apiRequest<ApplicationExternalLink>(
    `/api/applications/${applicationId}/links/${linkId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteApplicationLink(
  applicationId: string,
  linkId: string,
): Promise<void> {
  return apiRequest<void>(`/api/applications/${applicationId}/links/${linkId}`, {
    method: "DELETE",
  });
}
