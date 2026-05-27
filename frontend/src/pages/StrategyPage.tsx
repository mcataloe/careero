import {
  Alert,
  Badge,
  Box,
  Group,
  NavLink,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { useEffect, useMemo, useState } from "react";
import {
  NavLink as RouterNavLink,
  useNavigate,
  useParams,
} from "react-router-dom";

import { getCareerStrategy, getWorkspaceStrategy } from "../api/strategy";
import { listWorkspaces } from "../api/workspaces";
import { ErrorState, LoadingState } from "../components/States";
import type {
  CareerStrategySummary,
  SearchTrackStrategySummary,
  StrategySignal,
} from "../types/strategy";
import type { Workspace } from "../types/workspaces";

const strategySections = [
  {
    id: "overview",
    label: "Overview",
    description: "Summary, confidence, and sample size",
  },
  {
    id: "retrospective",
    label: "Retrospective",
    description: "What the stored track evidence says",
  },
  {
    id: "compensation",
    label: "Compensation",
    description: "Internal compensation alignment",
  },
  {
    id: "role-positioning",
    label: "Role positioning",
    description: "Market and role-pattern signals",
  },
  {
    id: "skill-gaps",
    label: "Skill gaps",
    description: "Repeated capability themes",
  },
  {
    id: "career-narrative",
    label: "Career narrative",
    description: "Positioning themes from stored data",
  },
  {
    id: "signals",
    label: "Strategy signals",
    description: "Current track-level signals",
  },
  {
    id: "actions",
    label: "Action candidates",
    description: "Advisory next steps",
  },
  {
    id: "uncertainty",
    label: "Uncertainty",
    description: "Warnings and thin-data notes",
  },
  {
    id: "cross-track",
    label: "Cross-track",
    description: "Comparison across stored tracks",
  },
] as const;

type StrategySectionId = (typeof strategySections)[number]["id"];

const sectionIds = new Set<string>(strategySections.map((section) => section.id));

export function StrategyPage() {
  const { workspaceId: routeWorkspaceId, section: sectionParam } = useParams();
  const navigate = useNavigate();
  const activeSection = isStrategySectionId(sectionParam) ? sectionParam : "overview";
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
    if (!isStrategySectionId(sectionParam)) {
      navigate(buildStrategyPath(routeWorkspaceId ?? selectedWorkspaceId, "overview"), {
        replace: true,
      });
    }
  }, [navigate, routeWorkspaceId, sectionParam, selectedWorkspaceId]);

  useEffect(() => {
    void loadStrategy(routeWorkspaceId);
  }, [routeWorkspaceId]);

  function handleWorkspaceChange(workspaceId: string | null) {
    if (!workspaceId) {
      return;
    }
    setSelectedWorkspaceId(workspaceId);
    navigate(buildStrategyPath(workspaceId, activeSection));
  }

  const sectionPathWorkspaceId = routeWorkspaceId ?? selectedWorkspaceId;

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Group gap="sm" align="center">
            <Title order={1}>Career strategy</Title>
            <Badge variant="light">Read-only</Badge>
          </Group>
          <Text c="dimmed">
            Focused strategy workspace based on stored Careero evidence.
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
        <div className="strategy-workspace">
          <StrategyLocalNavigation
            activeSection={activeSection}
            workspaceId={sectionPathWorkspaceId}
          />
          <Paper
            className="strategy-detail-panel"
            withBorder
            radius="md"
            p="lg"
          >
            <StrategySectionContent
              activeSection={activeSection}
              strategy={strategy}
              careerStrategy={careerStrategy}
            />
          </Paper>
        </div>
      ) : null}
    </Stack>
  );
}

function StrategyLocalNavigation({
  activeSection,
  workspaceId,
}: {
  activeSection: StrategySectionId;
  workspaceId: string | null;
}) {
  return (
    <Paper
      className="strategy-local-navigation"
      component="nav"
      aria-label="Career strategy sections"
      withBorder
      radius="md"
      p="sm"
    >
      <Stack gap={2}>
        {strategySections.map((section) => (
          <NavLink
            key={section.id}
            component={RouterNavLink}
            to={buildStrategyPath(workspaceId, section.id)}
            label={section.label}
            description={section.description}
            active={section.id === activeSection}
            aria-current={section.id === activeSection ? "page" : undefined}
          />
        ))}
      </Stack>
    </Paper>
  );
}

function StrategySectionContent({
  activeSection,
  strategy,
  careerStrategy,
}: {
  activeSection: StrategySectionId;
  strategy: SearchTrackStrategySummary;
  careerStrategy: CareerStrategySummary | null;
}) {
  switch (activeSection) {
    case "retrospective":
      return (
        <TextSection
          title="Retrospective"
          body={strategy.retrospective.summary}
          basis={strategy.retrospective.basis}
        />
      );
    case "compensation":
      return (
        <TextSection
          title="Compensation alignment"
          body={strategy.compensationAlignment.summary}
          basis={strategy.compensationAlignment.basis}
        />
      );
    case "role-positioning":
      return (
        <TextSection
          title="Role positioning"
          body={strategy.roleMarketPositioning.summary}
          basis={strategy.roleMarketPositioning.basis}
        />
      );
    case "skill-gaps":
      return <SignalSection title="Skill-gap themes" signals={strategy.skillGapThemes} />;
    case "career-narrative":
      return (
        <SignalSection
          title="Career narrative themes"
          signals={strategy.careerNarrativeThemes}
        />
      );
    case "signals":
      return <SignalSection title="Strategy signals" signals={strategy.signals} />;
    case "actions":
      return <ActionSection actions={strategy.actionCandidates} />;
    case "uncertainty":
      return (
        <UncertaintySection
          warnings={strategy.warnings}
          knownUncertainty={strategy.knownUncertainty}
          insufficientData={strategy.insufficientData}
        />
      );
    case "cross-track":
      return careerStrategy?.crossTrackComparison ? (
        <CrossTrackSection comparison={careerStrategy.crossTrackComparison} />
      ) : (
        <EmptySection
          title="Cross-track comparison"
          message="No cross-track comparison is available from stored data yet."
        />
      );
    case "overview":
    default:
      return <StrategyOverview strategy={strategy} />;
  }
}

function StrategyOverview({ strategy }: { strategy: SearchTrackStrategySummary }) {
  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-start" gap="md">
        <div>
          <Title order={2}>{strategy.workspaceName}</Title>
          <Text mt="xs">{strategy.summary}</Text>
        </div>
        <Badge variant="light">{formatConfidence(strategy.confidence.confidence)}</Badge>
      </Group>
      <Text c="dimmed" size="sm">
        {strategy.basis}
      </Text>
      <SimpleGrid cols={{ base: 2, sm: 3, md: 6 }} spacing="sm">
        <Metric label="Opportunities" value={strategy.sampleSize.opportunities} />
        <Metric label="Applications" value={strategy.sampleSize.applications} />
        <Metric
          label="Submitted"
          value={strategy.sampleSize.submittedApplications}
        />
        <Metric label="Responses" value={strategy.sampleSize.responses} />
        <Metric label="COMPASS" value={strategy.sampleSize.compassEvaluations} />
        <Metric
          label="Artifacts"
          value={strategy.sampleSize.artifactPerformanceRecords}
        />
      </SimpleGrid>
      {strategy.insufficientData.length > 0 ? (
        <Alert color="gray" title="Data is still thin">
          <Stack gap={4}>
            {strategy.insufficientData.map((item) => (
              <Text key={`${item.reason}-${item.message}`} size="sm">
                {item.message}
              </Text>
            ))}
          </Stack>
        </Alert>
      ) : null}
    </Stack>
  );
}

function CrossTrackSection({
  comparison,
}: {
  comparison: NonNullable<CareerStrategySummary["crossTrackComparison"]>;
}) {
  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={2}>Cross-track comparison</Title>
          <Text c="dimmed" size="sm">
            {comparison.basis}
          </Text>
        </div>
        <Badge variant="light">
          {formatConfidence(comparison.confidence.confidence)}
        </Badge>
      </Group>
      <Table verticalSpacing="sm">
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
        <Text key={warning} c="dimmed" size="xs">
          {warning}
        </Text>
      ))}
    </Stack>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <Box className="strategy-metric">
      <Text c="dimmed" size="xs">
        {label}
      </Text>
      <Text fw={700}>{value}</Text>
    </Box>
  );
}

function TextSection({
  title,
  body,
  basis,
}: {
  title: string;
  body: string;
  basis: string;
}) {
  return (
    <Stack gap="sm">
      <Title order={2}>{title}</Title>
      <Text>{body}</Text>
      <Text c="dimmed" size="xs">
        {basis}
      </Text>
    </Stack>
  );
}

function SignalSection({
  title,
  signals,
}: {
  title: string;
  signals: StrategySignal[];
}) {
  return (
    <Stack gap="md">
      <Title order={2}>{title}</Title>
      {signals.length > 0 ? (
        signals.map((signal) => (
          <Box key={signal.id}>
            <Group justify="space-between" align="flex-start">
              <Text fw={600}>{signal.label}</Text>
              <Badge variant="light">{formatConfidence(signal.confidence.confidence)}</Badge>
            </Group>
            <Text size="sm">{signal.message}</Text>
            <Text c="dimmed" size="xs">
              {signal.basis}
            </Text>
          </Box>
        ))
      ) : (
        <Text c="dimmed" size="sm">
          No current signal from stored data.
        </Text>
      )}
    </Stack>
  );
}

function ActionSection({
  actions,
}: {
  actions: SearchTrackStrategySummary["actionCandidates"];
}) {
  return (
    <Stack gap="md">
      <Title order={2}>Action candidates</Title>
      {actions.length > 0 ? (
        actions.map((action) => (
          <Box key={action.id}>
            <Text fw={600}>{action.title}</Text>
            <Text size="sm">{action.rationale}</Text>
            <Text c="dimmed" size="xs">
              {action.basis}
            </Text>
          </Box>
        ))
      ) : (
        <Text c="dimmed" size="sm">
          No advisory actions are active from the current evidence.
        </Text>
      )}
    </Stack>
  );
}

function UncertaintySection({
  warnings,
  knownUncertainty,
  insufficientData,
}: {
  warnings: string[];
  knownUncertainty: string[];
  insufficientData: SearchTrackStrategySummary["insufficientData"];
}) {
  return (
    <Stack gap="md">
      <Title order={2}>Warnings and uncertainty</Title>
      <ListGroup title="Warnings" items={warnings} />
      <ListGroup title="Known uncertainty" items={knownUncertainty} />
      <Stack gap="xs">
        <Title order={3}>Insufficient data</Title>
        {insufficientData.length > 0 ? (
          insufficientData.map((item) => (
            <Text key={`${item.reason}-${item.message}`} size="sm" c="dimmed">
              {item.message}
            </Text>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No additional thin-data notes are active.
          </Text>
        )}
      </Stack>
    </Stack>
  );
}

function ListGroup({ title, items }: { title: string; items: string[] }) {
  return (
    <Stack gap="xs">
      <Title order={3}>{title}</Title>
      {items.length > 0 ? (
        items.map((item) => (
          <Text key={item} size="sm" c="dimmed">
            {item}
          </Text>
        ))
      ) : (
        <Text c="dimmed" size="sm">
          None from the current evidence.
        </Text>
      )}
    </Stack>
  );
}

function EmptySection({ title, message }: { title: string; message: string }) {
  return (
    <Stack gap="sm">
      <Title order={2}>{title}</Title>
      <Text c="dimmed">{message}</Text>
    </Stack>
  );
}

function isStrategySectionId(value: string | undefined): value is StrategySectionId {
  return typeof value === "string" && sectionIds.has(value);
}

function buildStrategyPath(
  workspaceId: string | null | undefined,
  section: StrategySectionId,
) {
  return workspaceId
    ? `/workspaces/${workspaceId}/strategy/${section}`
    : `/strategy/${section}`;
}

function formatConfidence(value: string) {
  return value.replaceAll("_", " ");
}
