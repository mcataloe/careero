import { apiRequest, ApiError } from "./client";
import type { AdvisorPacket } from "../types/advisorPackets";

export function getAdvisorPacket(applicationId: string): Promise<AdvisorPacket> {
  return apiRequest<AdvisorPacket>(
    `/api/applications/${applicationId}/advisor-packet`,
  );
}

export async function exportAdvisorPacketMarkdown(applicationId: string): Promise<void> {
  const response = await fetch(
    `/api/applications/${applicationId}/advisor-packet/exports/md`,
    { method: "POST" },
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

function fileNameFromDisposition(response: Response): string | null {
  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename="([^"]+)"/);
  return match?.[1] ?? null;
}
