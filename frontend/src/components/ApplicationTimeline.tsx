import { Badge, Group, Paper, Stack, Text, Timeline } from "@mantine/core";

import type { ApplicationTimelineEvent } from "../types/applications";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function eventColor(eventType: string) {
  if (eventType.includes("archived")) {
    return "gray";
  }
  if (eventType.includes("reactivated")) {
    return "green";
  }
  if (eventType.includes("compass")) {
    return "violet";
  }
  if (eventType.includes("artifact")) {
    return "teal";
  }
  if (eventType.includes("reminder")) {
    return "orange";
  }
  if (eventType.includes("interview")) {
    return "blue";
  }
  return "dark";
}

const METADATA_LABELS: Record<string, string> = {
  from_state: "From",
  to_state: "To",
  state: "State",
  due_at: "Due",
  stage_type: "Stage",
  status: "Status",
  link_type: "Link",
  recommendation: "Recommendation",
  confidence: "Confidence",
  revision_number: "Revision",
  reactivate: "Reactivation",
};

function friendlyEventType(eventType: string) {
  return eventType.replaceAll(".", " ").replaceAll("_", " ");
}

function safeMetadataEntries(metadata: Record<string, unknown>) {
  return Object.entries(METADATA_LABELS)
    .map(([key, label]) => {
      const value = metadata[key];
      if (
        value === null ||
        value === undefined ||
        (typeof value !== "string" &&
          typeof value !== "number" &&
          typeof value !== "boolean")
      ) {
        return null;
      }
      return {
        key,
        label,
        value:
          key === "due_at" && typeof value === "string"
            ? formatDate(value)
            : String(value).replaceAll("_", " "),
      };
    })
    .filter(
      (entry): entry is { key: string; label: string; value: string } =>
        entry !== null,
    );
}

export function ApplicationTimeline({
  events,
}: {
  events: ApplicationTimelineEvent[];
}) {
  if (events.length === 0) {
    return (
      <Paper withBorder radius="md" p="lg">
        <Text c="dimmed" ta="center">
          No timeline events recorded yet.
        </Text>
      </Paper>
    );
  }

  return (
    <Timeline active={events.length} bulletSize={18} lineWidth={2}>
      {events.map((event) => (
        <Timeline.Item
          key={event.id}
          color={eventColor(event.event_type)}
          title={
            <Group gap="xs">
              <Text fw={600}>{event.title}</Text>
              <Badge size="xs" variant="light">
                {friendlyEventType(event.event_type)}
              </Badge>
            </Group>
          }
        >
          <Stack gap={4}>
            {event.description ? (
              <Text c="dimmed" size="sm">
                {event.description}
              </Text>
            ) : null}
            <Text c="dimmed" size="xs">
              {formatDate(event.occurred_at)} by {event.actor}
            </Text>
            {safeMetadataEntries(event.metadata).length > 0 ? (
              <Group gap="xs">
                {safeMetadataEntries(event.metadata).map((entry) => (
                  <Badge key={entry.key} size="xs" variant="outline">
                    {entry.label}: {entry.value}
                  </Badge>
                ))}
              </Group>
            ) : null}
          </Stack>
        </Timeline.Item>
      ))}
    </Timeline>
  );
}
