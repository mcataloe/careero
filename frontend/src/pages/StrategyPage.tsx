import {
  Alert,
  Badge,
  Group,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { useEffect, useMemo, useState } from "react";

import { getCareerStrategy, getWorkspaceStrategy } from "../api/strategy";
import { listWorkspaces } from "../api/workspaces";
import { ErrorState, LoadingState } from "../components/States";
import type {
  CareerStrategySummary,
  SearchTrackStrategySummary,
  StrategySignal,
} from "../types/strategy";
import type { Workspace } from "../types/workspaces";

export function StrategyPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | null>(null);
  const [strategy, setStrategy] = useState<SearchTrackStrategySummary | null>(null);
  const [careerStrategy, setCareerStrategy] =
    useState<CareerStrategySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const workspaceOptions = useMemo(
    () =>
      workspaces.map((workspace) => ({
        value: workspace.id,
        label: workspace.title,
      })),
    [workspaces],
  );

  async function loadStrategy(workspaceId?: string | null) {
    setLoading(true);
    setError(null);
    try {
      const workspaceList = await listWorkspaces({ includeInactive: true });
      setWorkspaces(workspaceList);
      const resolvedWorkspaceId = workspaceId ?? workspaceList[0]?.id ?? null;
      setSelectedWorkspaceId(resolvedWorkspaceId);
      const [workspaceStrategy, allStrategy] = await Promise.all([
        resolvedWorkspaceId ? getWorkspaceStrategy(resolvedWorkspaceId) : null,
        getCareerStrategy({ includeCrossTrack: true }),
      ]);
      setStrategy(workspaceStrategy);
      setCareerStrategy(allStrategy);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load strategy");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadStrategy();
  }, []);

  async function handleWorkspaceChange(workspaceId: string | null) {
    await loadStrategy(workspaceId);
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={1}>Career strategy</Title>
          <Text c="dimmed">
            Read-only strategy synthesis based on stored Careero evidence.
          </Text>
        </div>
        <Select
          aria-label="Workspace"
          data={workspaceOptions}
          value={selectedWorkspaceId}
          onChange={handleWorkspaceChange}
          placeholder="Select workspace"
          w={{ base: "100%", sm: 320 }}
        />
      </Group>

      {loading ? <LoadingState label="Loading strategy synthesis" /> : null}
      {!loading && error ? (
        <ErrorState message={error} onRetry={() => loadStrategy(selectedWorkspaceId)} />
      ) : null}
      {!loading && !error && !strategy ? (
        <Alert color="gray" title="No workspace strategy available">
          Add a workspace and save opportunities before strategy synthesis can review
          the track.
        </Alert>
      ) : null}
      {!loading && !error && strategy ? (
        <>
          <StrategyOverview strategy={strategy} />
          <StrategySections strategy={strategy} />
          {careerStrategy?.crossTrackComparison ? (
            <CrossTrackPanel comparison={careerStrategy.crossTrackComparison} />
          ) : null}
        </>
      ) : null}
    </Stack>
  );
}

function StrategyOverview({ strategy }: { strategy: SearchTrackStrategySummary }) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start" gap="md">
        <div>
          <Title order={2}>{strategy.workspaceName}</Title>
          <Text mt="xs">{strategy.summary}</Text>
        </div>
        <Badge variant="light">{formatConfidence(strategy.confidence.confidence)}</Badge>
      </Group>
      <Text c="dimmed" size="sm" mt="sm">
        {strategy.basis}
      </Text>
      <SimpleGrid cols={{ base: 2, sm: 3, md: 6 }} spacing="sm" mt="md">
        <Metric label="Opportunities" value={strategy.sampleSize.opportunities} />
        <Metric label="Applications" value={strategy.sampleSize.applications} />
        <Metric
          label="Submitted"
          value={strategy.sampleSize.submittedApplications}
        />
        <Metric label="Responses" value={strategy.sampleSize.responses} />
        <Metric label="STRIDE" value={strategy.sampleSize.strideEvaluations} />
        <Metric
          label="Artifacts"
          value={strategy.sampleSize.artifactPerformanceRecords}
        />
      </SimpleGrid>
      {strategy.insufficientData.length > 0 ? (
        <Alert color="gray" title="Data is still thin" mt="md">
          <Stack gap={4}>
            {strategy.insufficientData.map((item) => (
              <Text key={`${item.reason}-${item.message}`} size="sm">
                {item.message}
              </Text>
            ))}
          </Stack>
        </Alert>
      ) : null}
    </Paper>
  );
}

function StrategySections({ strategy }: { strategy: SearchTrackStrategySummary }) {
  return (
    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
      <TextPanel
        title="Retrospective"
        body={strategy.retrospective.summary}
        basis={strategy.retrospective.basis}
      />
      <TextPanel
        title="Compensation alignment"
        body={strategy.compensationAlignment.summary}
        basis={strategy.compensationAlignment.basis}
      />
      <TextPanel
        title="Role positioning"
        body={strategy.roleMarketPositioning.summary}
        basis={strategy.roleMarketPositioning.basis}
      />
      <SignalPanel title="Skill-gap themes" signals={strategy.skillGapThemes} />
      <SignalPanel
        title="Career narrative themes"
        signals={strategy.careerNarrativeThemes}
      />
      <SignalPanel title="Strategy signals" signals={strategy.signals} />
      <ActionPanel actions={strategy.actionCandidates} />
      <ListPanel title="Warnings and uncertainty" items={[...strategy.warnings, ...strategy.knownUncertainty]} />
    </SimpleGrid>
  );
}

function CrossTrackPanel({
  comparison,
}: {
  comparison: NonNullable<CareerStrategySummary["crossTrackComparison"]>;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={3}>Cross-track comparison</Title>
          <Text c="dimmed" size="sm">
            {comparison.basis}
          </Text>
        </div>
        <Badge variant="light">
          {formatConfidence(comparison.confidence.confidence)}
        </Badge>
      </Group>
      <Table mt="md" verticalSpacing="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Track</Table.Th>
            <Table.Th>Summary</Table.Th>
            <Table.Th>Signals</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {comparison.tracks.map((track) => (
            <Table.Tr key={track.workspaceId}>
              <Table.Td>{track.workspaceName}</Table.Td>
              <Table.Td>{track.summary}</Table.Td>
              <Table.Td>{track.signalCount}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      {comparison.warnings.map((warning) => (
        <Text key={warning} c="dimmed" size="xs" mt="xs">
          {warning}
        </Text>
      ))}
    </Paper>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <Paper withBorder radius="sm" p="sm">
      <Text c="dimmed" size="xs">
        {label}
      </Text>
      <Text fw={700}>{value}</Text>
    </Paper>
  );
}

function TextPanel({
  title,
  body,
  basis,
}: {
  title: string;
  body: string;
  basis: string;
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>{title}</Title>
      <Text mt="sm">{body}</Text>
      <Text c="dimmed" size="xs" mt="sm">
        {basis}
      </Text>
    </Paper>
  );
}

function SignalPanel({
  title,
  signals,
}: {
  title: string;
  signals: StrategySignal[];
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>{title}</Title>
      <Stack gap="sm" mt="md">
        {signals.length > 0 ? (
          signals.map((signal) => (
            <div key={signal.id}>
              <Group justify="space-between" align="flex-start">
                <Text fw={600}>{signal.label}</Text>
                <Badge variant="light">{formatConfidence(signal.confidence.confidence)}</Badge>
              </Group>
              <Text size="sm">{signal.message}</Text>
              <Text c="dimmed" size="xs">
                {signal.basis}
              </Text>
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No current signal from stored data.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function ActionPanel({ actions }: { actions: SearchTrackStrategySummary["actionCandidates"] }) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>Action candidates</Title>
      <Stack gap="sm" mt="md">
        {actions.length > 0 ? (
          actions.map((action) => (
            <div key={action.id}>
              <Text fw={600}>{action.title}</Text>
              <Text size="sm">{action.rationale}</Text>
              <Text c="dimmed" size="xs">
                {action.basis}
              </Text>
            </div>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No advisory actions are active from the current evidence.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function ListPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Title order={3}>{title}</Title>
      <Stack gap={4} mt="md">
        {items.map((item) => (
          <Text key={item} size="sm" c="dimmed">
            {item}
          </Text>
        ))}
      </Stack>
    </Paper>
  );
}

function formatConfidence(value: string) {
  return value.replaceAll("_", " ");
}
