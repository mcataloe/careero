import { apiRequest } from "./client";
import type {
  ArtifactDraftUpdatePayload,
  ArtifactRecord,
} from "../types/artifacts";

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
