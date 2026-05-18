import {
  Alert,
  Grid,
  Group,
  Paper,
  Stack,
  Table,
  Text,
  Title,
  Tooltip,
} from "@mantine/core";
import { useEffect, useState } from "react";

import { getSearchAnalytics } from "../api/searchAnalytics";
import { ErrorState, LoadingState } from "../components/States";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";

export function DashboardPage() {
  const [analytics, setAnalytics] = useState<SearchAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAnalytics() {
    setLoading(true);
    setError(null);
    try {
      setAnalytics(await getSearchAnalytics());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load analytics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAnalytics();
  }, []);

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Dashboard</Title>
        <Text c="dimmed">
          Search performance signals based on saved opportunities and application workflow activity.
        </Text>
      </div>

      {loading ? <LoadingState label="Loading search analytics" /> : null}
      {!loading && error ? (
        <ErrorState message={error} onRetry={loadAnalytics} />
      ) : null}
      {!loading && !error && analytics ? (
        <SearchAnalyticsPanel analytics={analytics} />
      ) : null}
    </Stack>
  );
}

function SearchAnalyticsPanel({
  analytics,
}: {
  analytics: SearchAnalyticsResponse;
}) {
  const summaryItems = [
    "opportunities_saved",
    "applications_submitted",
    "interviews_received",
    "response_latency_days",
    "followups_completed",
    "recruiter_contacts",
  ]
    .map((key) => analytics.summary[key])
    .filter(Boolean);

  return (
    <Stack gap="lg">
      {analytics.insufficient_data.length > 0 ? (
        <Alert color="gray" title="Data is still thin">
          <Stack gap={4}>
            {analytics.insufficient_data.map((message) => (
              <Text key={message} size="sm">
                {message}
              </Text>
            ))}
          </Stack>
        </Alert>
      ) : null}

      <Grid>
        {summaryItems.map((metric) => (
          <Grid.Col key={metric.label} span={{ base: 12, sm: 6, md: 4 }}>
            <Tooltip label={metric.basis} multiline maw={320}>
              <Paper withBorder radius="md" p="lg">
                <Text size="sm" c="dimmed">
                  {metric.label}
                </Text>
                <Title order={2} mt={4}>
                  {formatMetricValue(metric.value)}
                </Title>
              </Paper>
            </Tooltip>
          </Grid.Col>
        ))}
      </Grid>

      {analytics.signals.length > 0 ? (
        <Paper withBorder radius="md" p="lg">
          <Title order={3}>Focus signals</Title>
          <Stack mt="md" gap="sm">
            {analytics.signals.map((signal) => (
              <div key={String(signal.label)}>
                <Group justify="space-between" gap="sm">
                  <Text fw={600}>{String(signal.label)}</Text>
                  <Text size="xs" c="dimmed">
                    {String(signal.confidence)}
                  </Text>
                </Group>
                <Text size="sm" c="dimmed">
                  {String(signal.message)}
                </Text>
              </div>
            ))}
          </Stack>
        </Paper>
      ) : null}

      <Paper withBorder radius="md" p="lg">
        <Title order={3}>Stage conversion</Title>
        <Table mt="md" verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Movement</Table.Th>
              <Table.Th>Rate</Table.Th>
              <Table.Th>Basis</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {analytics.conversion_rates.map((metric) => (
              <Table.Tr key={`${metric.from_stage}-${metric.to_stage}`}>
                <Table.Td>
                  {formatStage(metric.from_stage)} to {formatStage(metric.to_stage)}
                </Table.Td>
                <Table.Td>{formatRate(metric.rate)}</Table.Td>
                <Table.Td>
                  {metric.numerator} of {metric.denominator}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}

function formatMetricValue(value: number | null) {
  if (value === null) return "Not enough data";
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatRate(value: number | null) {
  if (value === null) return "Not enough data";
  return `${Math.round(value * 100)}%`;
}

function formatStage(value: string) {
  return value.replaceAll("_", " ");
}
