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
import { listAutomationSuggestions } from "../api/automation";
import { getCompensationIntelligence } from "../api/compensationIntelligence";
import { getHistoricalLearning } from "../api/historicalLearning";
import { getRecommendations } from "../api/recommendations";
import { getSearchAnalytics } from "../api/searchAnalytics";
import { getSearchHealth } from "../api/searchHealth";
import { getSourceIntelligence } from "../api/sourceIntelligence";
import { getCompassInsights } from "../api/compassInsights";
import { ErrorState, LoadingState } from "../components/States";
import { AutomationSuggestionsPanel } from "../components/AutomationSuggestionsPanel";
import { InsightMeta } from "../components/InsightMeta";
import type { ArtifactPerformanceResponse } from "../types/artifactPerformance";
import type { AutomationSuggestionListResponse } from "../types/automation";
import type { CompensationIntelligenceResponse } from "../types/compensationIntelligence";
import type { HistoricalLearningResponse } from "../types/historicalLearning";
import type { RecommendationListResponse } from "../types/recommendations";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";
import type { SearchHealthResponse } from "../types/searchHealth";
import type { SourceIntelligenceResponse } from "../types/sourceIntelligence";
import type { CompassInsightsResponse } from "../types/compassInsights";

export function DashboardPage() {
  const [analytics, setAnalytics] = useState<SearchAnalyticsResponse | null>(null);
  const [artifactPerformance, setArtifactPerformance] =
    useState<ArtifactPerformanceResponse | null>(null);
  const [compassInsights, setCompassInsights] =
    useState<CompassInsightsResponse | null>(null);
  const [sourceIntelligence, setSourceIntelligence] =
    useState<SourceIntelligenceResponse | null>(null);
  const [compensationIntelligence, setCompensationIntelligence] =
    useState<CompensationIntelligenceResponse | null>(null);
  const [searchHealth, setSearchHealth] = useState<SearchHealthResponse | null>(null);
  const [recommendations, setRecommendations] =
    useState<RecommendationListResponse | null>(null);
  const [historicalLearning, setHistoricalLearning] =
    useState<HistoricalLearningResponse | null>(null);
  const [automationSuggestions, setAutomationSuggestions] =
    useState<AutomationSuggestionListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAnalytics() {
    setLoading(true);
    setError(null);
    try {
      const [
        searchAnalytics,
        artifactAnalytics,
        compassAnalytics,
        sourceAnalytics,
        compensationAnalytics,
        searchHealthAnalytics,
        recommendationData,
        historicalData,
        automationData,
      ] = await Promise.all([
        getSearchAnalytics(),
        getArtifactPerformance(),
        getCompassInsights(),
        getSourceIntelligence(),
        getCompensationIntelligence(),
        getSearchHealth(),
        getRecommendations(),
        getHistoricalLearning(),
        listAutomationSuggestions(),
      ]);
      setAnalytics(searchAnalytics);
      setArtifactPerformance(artifactAnalytics);
      setCompassInsights(compassAnalytics);
      setSourceIntelligence(sourceAnalytics);
      setCompensationIntelligence(compensationAnalytics);
      setSearchHealth(searchHealthAnalytics);
      setRecommendations(recommendationData);
      setHistoricalLearning(historicalData);
      setAutomationSuggestions(automationData);
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
          {compassInsights ? <CompassInsightsPanel insights={compassInsights} /> : null}
          {sourceIntelligence ? (
            <SourceIntelligencePanel intelligence={sourceIntelligence} />
          ) : null}
          {compensationIntelligence ? (
            <CompensationIntelligencePanel
              intelligence={compensationIntelligence}
            />
          ) : null}
          {searchHealth ? <SearchHealthPanel health={searchHealth} /> : null}
          {recommendations ? (
            <RecommendationsPanel recommendations={recommendations} />
          ) : null}
          {automationSuggestions ? (
            <AutomationSuggestionsPanel
              suggestions={automationSuggestions.suggestions}
              onChanged={loadAnalytics}
            />
          ) : null}
          {historicalLearning ? (
            <HistoricalLearningPanel learning={historicalLearning} />
          ) : null}
        </>
      ) : null}
    </Stack>
  );
}

function HistoricalLearningPanel({
  learning,
}: {
  learning: HistoricalLearningResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Historical learning</Title>
      <Text c="dimmed" size="sm" mt="xs">
        Patterns from completed, archived, and prior tracked search activity.
      </Text>
      <Table mt="md" verticalSpacing="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Question</Table.Th>
            <Table.Th>Observed answer</Table.Th>
            <Table.Th>Confidence</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {learning.summaries.length > 0 ? (
            learning.summaries.slice(0, 8).map((summary) => (
              <Table.Tr key={summary.label}>
                <Table.Td>{summary.label}</Table.Td>
                <Table.Td>{summary.value ?? "Not enough data"}</Table.Td>
                <Table.Td>{summary.confidence}</Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={3}>
                <Text c="dimmed" size="sm">
                  Archive or complete a search track to build reusable historical learning.
                </Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Paper>
  );
}

function RecommendationsPanel({
  recommendations,
}: {
  recommendations: RecommendationListResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Recommendations</Title>
      <Text c="dimmed" size="sm" mt="xs">
        Read-only next steps with visible reasons.
      </Text>
      <Stack gap="sm" mt="md">
        {recommendations.recommendations.length > 0 ? (
          recommendations.recommendations.slice(0, 8).map((recommendation) => (
            <div key={recommendation.id}>
              <Text fw={600}>{recommendation.title}</Text>
              <Text size="sm" c="dimmed">
                {recommendation.action.replaceAll("_", " ")}:{" "}
                {recommendation.reason}
              </Text>
              <InsightMeta
                confidence={recommendation.confidence}
                basis={recommendation.basis}
              />
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No recommendations are active from the current insight signals.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function SearchHealthPanel({ health }: { health: SearchHealthResponse }) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Search health</Title>
      <Text c="dimmed" size="sm" mt="xs">
        Gentle sustainability signals based on tracked search activity.
      </Text>
      <Stack gap="sm" mt="md">
        {health.signals.length > 0 ? (
          health.signals.map((signal) => (
            <div key={signal.signal_type}>
              <Group justify="space-between" align="flex-start">
                <Text fw={600}>{signal.label}</Text>
                <Badge variant="light">{signal.confidence}</Badge>
              </Group>
              <Text size="sm" c="dimmed">
                {signal.message}
              </Text>
              <Text size="sm">{signal.gentle_guidance}</Text>
              <Text size="xs" c="dimmed">
                {signal.basis}
              </Text>
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No search-health signals are active from the current tracked activity.
          </Text>
        )}
      </Stack>
    </Paper>
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
            Add stated compensation ranges to saved opportunities to compare against search-track targets.
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

function CompassInsightsPanel({
  insights,
}: {
  insights: CompassInsightsResponse;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={3}>COMPASS search trends</Title>
          <Text c="dimmed" size="sm">
            Average score:{" "}
            {insights.average_compass_score === null
              ? "Not enough data"
              : insights.average_compass_score.toFixed(1)}
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
            Complete COMPASS evaluations to build search-level trend insight.
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
