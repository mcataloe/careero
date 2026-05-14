import { ApiError, apiRequest } from "./client";
import type {
  ActiveResumeSource,
  ResumeSource,
  ResumeSourceCreatePayload,
  ResumeSourceImportResponse,
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

export async function importResumeSourceFile(
  file: File,
): Promise<ResumeSourceImportResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/resume-sources/import", {
    method: "POST",
    body: formData,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String(data.detail)
        : `Request failed with status ${response.status}`;
    throw new ApiError(detail, response.status);
  }

  return data as ResumeSourceImportResponse;
}
