import { TimelineEvent } from "../types/timeline";

export async function getApplicationTimeline(
  applicationId: string,
): Promise<TimelineEvent[]> {
  const response = await fetch(`/api/applications/${applicationId}/timeline`);

  if (!response.ok) {
    throw new Error(`Failed to load timeline: ${response.statusText}`);
  }

  return response.json();
}
