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
                {event.event_type}
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
          </Stack>
        </Timeline.Item>
      ))}
    </Timeline>
  );
}
