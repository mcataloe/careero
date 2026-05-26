import { apiRequest } from "./client";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationExternalLinkPayload,
  ApplicationInterviewCancelPayload,
  ApplicationInterviewCompletePayload,
  ApplicationInterviewStage,
  ApplicationInterviewStagePayload,
  ApplicationNote,
  ApplicationNotePayload,
  ApplicationPipelineResponse,
  ApplicationReminder,
  ApplicationReminderPayload,
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

export function listApplicationReminders(
  applicationId: string,
): Promise<ApplicationReminder[]> {
  return apiRequest<ApplicationReminder[]>(
    `/api/applications/${applicationId}/reminders`,
  );
}

export function createApplicationReminder(
  applicationId: string,
  payload: ApplicationReminderPayload,
): Promise<ApplicationReminder> {
  return apiRequest<ApplicationReminder>(
    `/api/applications/${applicationId}/reminders`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateApplicationReminder(
  applicationId: string,
  reminderId: string,
  payload: Partial<ApplicationReminderPayload>,
): Promise<ApplicationReminder> {
  return apiRequest<ApplicationReminder>(
    `/api/applications/${applicationId}/reminders/${reminderId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function completeApplicationReminder(
  applicationId: string,
  reminderId: string,
): Promise<ApplicationReminder> {
  return apiRequest<ApplicationReminder>(
    `/api/applications/${applicationId}/reminders/${reminderId}/complete`,
    {
      method: "POST",
    },
  );
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


export function listApplicationInterviews(
  applicationId: string,
): Promise<ApplicationInterviewStage[]> {
  return apiRequest<ApplicationInterviewStage[]>(
    `/api/applications/${applicationId}/interviews`,
  );
}

export function createApplicationInterview(
  applicationId: string,
  payload: ApplicationInterviewStagePayload,
): Promise<ApplicationInterviewStage> {
  return apiRequest<ApplicationInterviewStage>(
    `/api/applications/${applicationId}/interviews`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateApplicationInterview(
  applicationId: string,
  interviewId: string,
  payload: Partial<ApplicationInterviewStagePayload>,
): Promise<ApplicationInterviewStage> {
  return apiRequest<ApplicationInterviewStage>(
    `/api/applications/${applicationId}/interviews/${interviewId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function completeApplicationInterview(
  applicationId: string,
  interviewId: string,
  payload: ApplicationInterviewCompletePayload = {},
): Promise<ApplicationInterviewStage> {
  return apiRequest<ApplicationInterviewStage>(
    `/api/applications/${applicationId}/interviews/${interviewId}/complete`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function cancelApplicationInterview(
  applicationId: string,
  interviewId: string,
  payload: ApplicationInterviewCancelPayload = {},
): Promise<ApplicationInterviewStage> {
  return apiRequest<ApplicationInterviewStage>(
    `/api/applications/${applicationId}/interviews/${interviewId}/cancel`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteApplicationInterview(
  applicationId: string,
  interviewId: string,
): Promise<void> {
  return apiRequest<void>(
    `/api/applications/${applicationId}/interviews/${interviewId}`,
    { method: "DELETE" },
  );
}
