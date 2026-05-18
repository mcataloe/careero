import {
  Alert,
  Badge,
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

import { getArtifactPerformance } from "../api/artifactPerformance";
import { getCompensationIntelligence } from "../api/compensationIntelligence";
import { getSearchAnalytics } from "../api/searchAnalytics";
import { getSourceIntelligence } from "../api/sourceIntelligence";
import { getStrideInsights } from "../api/strideInsights";
import { ErrorState, LoadingState } from "../components/States";
import type { ArtifactPerformanceResponse } from "../types/artifactPerformance";
import type { CompensationIntelligenceResponse } from "../types/compensationIntelligence";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";
import type { SourceIntelligenceResponse } from "../types/sourceIntelligence";
import type { StrideInsightsResponse } from "../types/strideInsights";

export function DashboardPage() {
  const [analytics, setAnalytics] = useState<SearchAnalyticsResponse | null>(null);
  const [artifactPerformance, setArtifactPerformance] =
    useState<ArtifactPerformanceResponse | null>(null);
  const [strideInsights, setStrideInsights] =
    useState<StrideInsightsResponse | null>(null);
  const [sourceIntelligence, setSourceIntelligence] =
    useState<SourceIntelligenceResponse | null>(null);
  const [compensationIntelligence, setCompensationIntelligence] =
    useState<CompensationIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAnalytics() {
    setLoading(true);
    setError(null);
    try {
      const [
        searchAnalytics,
        artifactAnalytics,
        strideAnalytics,
        sourceAnalytics,
        compensationAnalytics,
      ] = await Promise.all([
        getSearchAnalytics(),
        getArtifactPerformance(),
        getStrideInsights(),
        getSourceIntelligence(),
        getCompensationIntelligence(),
      ]);
      setAnalytics(searchAnalytics);
      setArtifactPerformance(artifactAnalytics);
      setStrideInsights(strideAnalytics);
      setSourceIntelligence(sourceAnalytics);
      setCompensationIntelligence(compensationAnalytics);
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
        <>
          <SearchAnalyticsPanel analytics={analytics} />
          {artifactPerformance ? (
            <ArtifactPerformancePanel performance={artifactPerformance} />
          ) : null}
          {strideInsights ? <StrideInsightsPanel insights={strideInsights} /> : null}
          {sourceIntelligence ? (
            <SourceIntelligencePanel intelligence={sourceIntelligence} />
          ) : null}
          {compensationIntelligence ? (
            <CompensationIntelligencePanel
              intelligence={compensationIntelligence}
            />
          ) : null}
        </>
      ) : null}
    </Stack>
  );
}

function CompensationIntelligencePanel({
  intelligence,
}: {
  intelligence: CompensationIntelligenceResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Compensation intelligence</Title>
      <Text c="dimmed" size="sm" mt="xs">
        Uses stated ranges only; no external salary guesses are generated.
      </Text>
      <Stack gap="sm" mt="md">
        {intelligence.insights.length > 0 ? (
          intelligence.insights.map((insight) => (
            <div key={insight.label}>
              <Group justify="space-between" align="flex-start">
                <Text fw={600}>{insight.label}</Text>
                <Badge variant="light">{insight.confidence}</Badge>
              </Group>
              <Text size="sm" c="dimmed">
                {insight.message}
              </Text>
              <Text size="xs" c="dimmed">
                {insight.basis}
              </Text>
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            Add stated compensation ranges to saved roles to compare against search-track targets.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function SourceIntelligencePanel({
  intelligence,
}: {
  intelligence: SourceIntelligenceResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Recruiter & source intelligence</Title>
      <Text c="dimmed" size="sm" mt="xs">
        Private source performance based on your own tracked opportunities.
      </Text>
      <Table mt="md" verticalSpacing="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Source</Table.Th>
            <Table.Th>Applications</Table.Th>
            <Table.Th>Response rate</Table.Th>
            <Table.Th>Recruiter contacts</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {intelligence.summaries.length > 0 ? (
            intelligence.summaries.map((summary) => (
              <Table.Tr key={summary.source_type}>
                <Table.Td>{summary.label}</Table.Td>
                <Table.Td>{summary.applications}</Table.Td>
                <Table.Td>{formatRate(summary.response_rate)}</Table.Td>
                <Table.Td>{summary.recruiter_contacts}</Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={4}>
                <Text c="dimmed" size="sm">
                  Add source metadata to opportunities to compare private traction by channel.
                </Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Paper>
  );
}

function StrideInsightsPanel({
  insights,
}: {
  insights: StrideInsightsResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={3}>STRIDE search trends</Title>
          <Text c="dimmed" size="sm">
            Average score:{" "}
            {insights.average_stride_score === null
              ? "Not enough data"
              : insights.average_stride_score.toFixed(1)}
          </Text>
        </div>
      </Group>
      <Stack gap="sm" mt="md">
        {insights.insights.length > 0 ? (
          insights.insights.map((insight) => (
            <div key={insight.label}>
              <Group justify="space-between" align="flex-start">
                <Text fw={600}>{insight.label}</Text>
                <Badge variant="light">{insight.confidence}</Badge>
              </Group>
              <Text size="sm" c="dimmed">
                {insight.message}
              </Text>
              <Text size="xs" c="dimmed">
                {insight.basis}
              </Text>
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            Complete STRIDE evaluations to build search-level trend insight.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function ArtifactPerformancePanel({
  performance,
}: {
  performance: ArtifactPerformanceResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Artifact performance</Title>
      {performance.insufficient_data.length > 0 ? (
        <Text c="dimmed" size="sm" mt="xs">
          {performance.insufficient_data[0]}
        </Text>
      ) : null}
      <Table mt="md" verticalSpacing="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Variant</Table.Th>
            <Table.Th>Uses</Table.Th>
            <Table.Th>Response rate</Table.Th>
            <Table.Th>Interview rate</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {performance.by_variant.length > 0 ? (
            performance.by_variant.slice(0, 6).map((metric) => (
              <Table.Tr key={metric.label}>
                <Table.Td>{metric.label}</Table.Td>
                <Table.Td>{metric.total}</Table.Td>
                <Table.Td>{formatRate(metric.response_rate)}</Table.Td>
                <Table.Td>{formatRate(metric.interview_rate)}</Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={4}>
                <Text c="dimmed" size="sm">
                  Generate and use resume or cover-letter artifacts to build observed performance history.
                </Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Paper>
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
