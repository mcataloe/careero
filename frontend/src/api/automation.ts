import { apiRequest } from "./client";
import type {
  AutomationApprovalLog,
  AutomationApprovalLogListResponse,
  AutomationPreferences,
  AutomationPreferencesPayload,
  AutomationSuggestionListResponse,
} from "../types/automation";

function appendSuggestionParams(
  path: string,
  {
    workspaceId,
    targetType,
    targetId,
  }: {
    workspaceId?: string | null;
    targetType?: string | null;
    targetId?: string | null;
  } = {},
) {
  const params = new URLSearchParams();
  if (workspaceId) params.set("workspace_id", workspaceId);
  if (targetType) params.set("target_type", targetType);
  if (targetId) params.set("target_id", targetId);
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

export function listAutomationSuggestions(options?: {
  workspaceId?: string | null;
  targetType?: string | null;
  targetId?: string | null;
}): Promise<AutomationSuggestionListResponse> {
  return apiRequest<AutomationSuggestionListResponse>(
    appendSuggestionParams("/api/automation/suggestions", options),
  );
}

export function approveAutomationSuggestion(
  suggestionId: string,
): Promise<AutomationApprovalLog> {
  return apiRequest<AutomationApprovalLog>(
    `/api/automation/suggestions/${suggestionId}/approve`,
    {
      method: "POST",
      body: JSON.stringify({ actor: "user" }),
    },
  );
}

export function rejectAutomationSuggestion(
  suggestionId: string,
  reason?: string | null,
): Promise<AutomationApprovalLog> {
  return apiRequest<AutomationApprovalLog>(
    `/api/automation/suggestions/${suggestionId}/reject`,
    {
      method: "POST",
      body: JSON.stringify({ actor: "user", reason: reason ?? null }),
    },
  );
}

export function dismissAutomationSuggestion(
  suggestionId: string,
  reason?: string | null,
): Promise<AutomationApprovalLog> {
  return apiRequest<AutomationApprovalLog>(
    `/api/automation/suggestions/${suggestionId}/dismiss`,
    {
      method: "POST",
      body: JSON.stringify({ actor: "user", reason: reason ?? null }),
    },
  );
}

export function listAutomationApprovalLogs(options?: {
  workspaceId?: string | null;
}): Promise<AutomationApprovalLogListResponse> {
  const params = new URLSearchParams();
  if (options?.workspaceId) params.set("workspace_id", options.workspaceId);
  const query = params.toString();
  return apiRequest<AutomationApprovalLogListResponse>(
    query ? `/api/automation/approval-logs?${query}` : "/api/automation/approval-logs",
  );
}

export function getAutomationPreferences(
  workspaceId: string,
): Promise<AutomationPreferences> {
  return apiRequest<AutomationPreferences>(
    `/api/workspaces/${workspaceId}/automation-preferences`,
  );
}

export function updateAutomationPreferences(
  workspaceId: string,
  payload: AutomationPreferencesPayload,
): Promise<AutomationPreferences> {
  return apiRequest<AutomationPreferences>(
    `/api/workspaces/${workspaceId}/automation-preferences`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}
