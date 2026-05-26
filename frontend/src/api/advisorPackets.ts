import { apiRequest, ApiError } from "./client";
import type {
  AdvisorPacket,
  AdvisorPacketPreviewOptions,
} from "../types/advisorPackets";

export function getAdvisorPacket(
  applicationId: string,
  options: AdvisorPacketPreviewOptions = {},
): Promise<AdvisorPacket> {
  if (hasPreviewOptions(options)) {
    return apiRequest<AdvisorPacket>(
      `/api/applications/${applicationId}/advisor-packet/preview`,
      {
        method: "POST",
        body: JSON.stringify(packetBody(options)),
      },
    );
  }

  return apiRequest<AdvisorPacket>(
    `/api/applications/${applicationId}/advisor-packet`,
  );
}

export async function exportAdvisorPacketMarkdown(
  applicationId: string,
  options: AdvisorPacketPreviewOptions = {},
): Promise<void> {
  const response = await fetch(
    `/api/applications/${applicationId}/advisor-packet/exports/md`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(packetBody(options)),
    },
  );
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const data = await response.json();
      if (data && typeof data === "object" && "detail" in data) {
        message = String(data.detail);
      }
    }
    throw new ApiError(message, response.status);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileNameFromDisposition(response) ?? "careero-advisor-packet.md";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function hasPreviewOptions(options: AdvisorPacketPreviewOptions): boolean {
  return Boolean(
    options.artifactIds?.length ||
      options.externalLinkIds?.length ||
      options.interviewStageIds?.length ||
      options.reminderIds?.length ||
      options.advisorContext?.trim(),
  );
}

function packetBody(options: AdvisorPacketPreviewOptions) {
  return {
    artifact_ids: options.artifactIds ?? [],
    external_link_ids: options.externalLinkIds ?? [],
    interview_stage_ids: options.interviewStageIds ?? [],
    reminder_ids: options.reminderIds ?? [],
    advisor_context: options.advisorContext?.trim() || null,
  };
}

function fileNameFromDisposition(response: Response): string | null {
  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename="([^"]+)"/);
  return match?.[1] ?? null;
}
