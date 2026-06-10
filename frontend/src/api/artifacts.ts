import { ApiError, apiRequest } from "./client";
import type {
  ArtifactDraftUpdatePayload,
  ArtifactRecord,
} from "../types/artifacts";

export type ArtifactExportFormat = "md" | "docx" | "pdf";

export interface ArtifactExportDownload {
  blob: Blob;
  filename: string;
  contentHash: string | null;
  format: ArtifactExportFormat;
}

export function listApplicationArtifacts(
  applicationId: string,
  options: { includeArchived?: boolean } = {},
): Promise<ArtifactRecord[]> {
  const params = new URLSearchParams();
  if (options.includeArchived) {
    params.set("include_archived", "true");
  }
  const query = params.toString();
  return apiRequest<ArtifactRecord[]>(
    `/api/applications/${applicationId}/artifacts${query ? `?${query}` : ""}`,
  );
}

export function updateArtifactDraft(
  artifactId: string,
  payload: ArtifactDraftUpdatePayload,
): Promise<ArtifactRecord> {
  return apiRequest<ArtifactRecord>(`/api/artifacts/${artifactId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function markArtifactReviewed(artifactId: string): Promise<ArtifactRecord> {
  return apiRequest<ArtifactRecord>(`/api/artifacts/${artifactId}/review`, {
    method: "POST",
  });
}

export function markArtifactSubmitted(artifactId: string): Promise<ArtifactRecord> {
  return apiRequest<ArtifactRecord>(`/api/artifacts/${artifactId}/submit`, {
    method: "POST",
  });
}

export function archiveArtifact(artifactId: string): Promise<ArtifactRecord> {
  return apiRequest<ArtifactRecord>(`/api/artifacts/${artifactId}/archive`, {
    method: "POST",
  });
}

export async function downloadArtifactExport(
  artifactId: string,
  format: ArtifactExportFormat,
): Promise<ArtifactExportDownload> {
  const response = await fetch(`/api/artifacts/${artifactId}/exports/${format}`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new ApiError(await readExportError(response), response.status);
  }

  const blob = await response.blob();
  return {
    blob,
    filename:
      filenameFromContentDisposition(response.headers.get("content-disposition")) ??
      `careero-artifact.${format}`,
    contentHash: response.headers.get("x-careero-content-hash"),
    format,
  };
}

async function readExportError(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    const data = await response.json();
    if (typeof data === "object" && data !== null && "detail" in data) {
      return String(data.detail);
    }
  } else {
    const text = await response.text();
    if (text.trim()) {
      return text;
    }
  }
  return `Artifact export failed with status ${response.status}`;
}

function filenameFromContentDisposition(value: string | null) {
  if (!value) {
    return null;
  }

  const utf8Filename = value.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Filename?.[1]) {
    try {
      return decodeURIComponent(utf8Filename[1]);
    } catch {
      return utf8Filename[1];
    }
  }

  const quotedFilename = value.match(/filename="([^"]+)"/i);
  if (quotedFilename?.[1]) {
    return quotedFilename[1];
  }

  const plainFilename = value.match(/filename=([^;]+)/i);
  return plainFilename?.[1]?.trim() ?? null;
}
