import React from "react";
import { Timeline, Text, Paper, ThemeIcon, Stack } from "@mantine/core";
import { TimelineEvent } from "../types/timeline";

interface ApplicationTimelineProps {
  events: TimelineEvent[];
}

export const ApplicationTimeline: React.FC<ApplicationTimelineProps> = ({
  events,
}) => {
  if (!events || events.length === 0) {
    return (
      <Paper withBorder p="md" radius="md">
        <Text color="dimmed" align="center" size="sm">
          No timeline events recorded yet.
        </Text>
      </Paper>
    );
  }

  return (
    <Stack spacing="md">
      <Timeline active={events.length} bulletSize={24} lineWidth={2}>
        {events.map((event) => {
          const dateStr = new Date(event.occurredAt).toLocaleString();

          // Simple deterministic color and icon strategy based on eventType
          let color = "blue";
          if (event.eventType.includes("created")) color = "teal";
          if (event.eventType.includes("archived")) color = "gray";
          if (event.eventType.includes("withdrawn")) color = "orange";
          if (event.eventType.includes("rejected")) color = "red";
          if (event.eventType.includes("stride")) color = "violet";

          return (
            <Timeline.Item key={event.id} title={event.title} color={color}>
              {event.description && (
                <Text color="dimmed" size="sm" mt={4}>
                  {event.description}
                </Text>
              )}
              <Text size="xs" mt={4} color="dimmed">
                {dateStr} •{" "}
                {event.actor === "automation" ? "🤖 AI Automation" : "👤 User"}
              </Text>
            </Timeline.Item>
          );
        })}
      </Timeline>
    </Stack>
  );
};
