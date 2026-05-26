import { Badge, Group, Paper, SimpleGrid, Stack, Table, Text, Title } from "@mantine/core";
import { IconBolt } from "@tabler/icons-react";
import { useEffect, useState } from "react";

import { listAIUsage } from "../api/aiUsage";
import { ErrorState, LoadingState } from "./States";
import type { AIUsageEvent, AIUsageList } from "../types/aiUsage";

function formatValue(value: string) {
  return value.replaceAll("_", " ");
}

function modelLabel(event: AIUsageEvent) {
  if (!event.provider && !event.model) {
    return "Local/deterministic";
  }
  return [event.provider, event.model].filter(Boolean).join(" / ");
}

export function AIUsagePanel() {
  const [usage, setUsage] = useState<AIUsageList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadUsage() {
    setLoading(true);
    setError(null);
    try {
      setUsage(await listAIUsage());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load AI usage");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUsage();
  }, []);

  if (loading) {
    return <LoadingState label="Loading AI usage" />;
  }

  if (error && !usage) {
    return <ErrorState message={error} onRetry={loadUsage} />;
  }

  if (!usage) {
    return null;
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>AI usage</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Local metadata for AI requests, skips, cache reuse, and failures.
            </Text>
          </div>
          <Badge leftSection={<IconBolt size={14} />} variant="light">
            {usage.summary.total_events} events
          </Badge>
        </Group>

        <Text size="sm">{usage.usage_note}</Text>

        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="sm">
          <div>
            <Text size="xs" c="dimmed">
              By feature
            </Text>
            <Text size="sm">
              {Object.entries(usage.summary.by_feature)
                .map(([feature, count]) => `${formatValue(feature)}: ${count}`)
                .join(", ") || "No usage recorded"}
            </Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              By event
            </Text>
            <Text size="sm">
              {Object.entries(usage.summary.by_event_type)
                .map(([eventType, count]) => `${formatValue(eventType)}: ${count}`)
                .join(", ") || "No usage recorded"}
            </Text>
          </div>
        </SimpleGrid>

        {usage.events.length === 0 ? (
          <Text c="dimmed" size="sm">
            No local AI usage events have been recorded.
          </Text>
        ) : (
          <Table.ScrollContainer minWidth={720}>
            <Table verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Feature</Table.Th>
                  <Table.Th>Event</Table.Th>
                  <Table.Th>Model</Table.Th>
                  <Table.Th>Tokens</Table.Th>
                  <Table.Th>Created</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {usage.events.map((event) => (
                  <Table.Tr key={event.id}>
                    <Table.Td>{formatValue(event.feature)}</Table.Td>
                    <Table.Td>{formatValue(event.event_type)}</Table.Td>
                    <Table.Td>{modelLabel(event)}</Table.Td>
                    <Table.Td>
                      {event.input_token_estimate ?? 0} in /{" "}
                      {event.output_token_estimate ?? 0} out
                    </Table.Td>
                    <Table.Td>{new Date(event.created_at).toLocaleString()}</Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Stack>
    </Paper>
  );
}
