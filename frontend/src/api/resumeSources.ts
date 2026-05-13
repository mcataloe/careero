import { ApiError, apiRequest } from "./client";
import type {
  ActiveResumeSource,
  ResumeSource,
  ResumeSourceCreatePayload,
  ResumeSourceVersion,
  ResumeSourceVersionCreatePayload,
} from "../types/resumeSources";

export async function getActiveResumeSource(): Promise<ActiveResumeSource | null> {
  try {
    return await apiRequest<ActiveResumeSource>("/api/resume-sources/active");
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export function createResumeSource(
  payload: ResumeSourceCreatePayload,
): Promise<ResumeSource> {
  return apiRequest<ResumeSource>("/api/resume-sources", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createResumeSourceVersion(
  sourceId: string,
  payload: ResumeSourceVersionCreatePayload,
): Promise<ResumeSourceVersion> {
  return apiRequest<ResumeSourceVersion>(`/api/resume-sources/${sourceId}/versions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function activateResumeSourceVersion(
  sourceId: string,
  versionId: string,
): Promise<ResumeSourceVersion> {
  return apiRequest<ResumeSourceVersion>(
    `/api/resume-sources/${sourceId}/versions/${versionId}/activate`,
    { method: "POST" },
  );
}
