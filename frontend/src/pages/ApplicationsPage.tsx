import {
  Badge,
  Button,
  Card,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Switch,
  Text,
  Title,
} from "@mantine/core";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  getApplicationsPipeline,
  transitionApplicationState,
} from "../api/applications";
import { ErrorState, LoadingState } from "../components/States";
import type {
  ApplicationPipelineResponse,
  ApplicationSummary,
  ApplicationWorkflowState,
} from "../types/applications";

const ACTIVE_STATES: ApplicationWorkflowState[] = [
  "discovered",
  "interested",
  "applied",
  "interviewing",
  "offer",
  "rejected",
  "withdrawn",
];

const ALL_STATES: ApplicationWorkflowState[] = [...ACTIVE_STATES, "archived"];

const STATE_COLORS: Record<ApplicationWorkflowState, string> = {
  discovered: "gray",
  interested: "blue",
  applied: "teal",
  interviewing: "violet",
  offer: "green",
  rejected: "red",
  withdrawn: "orange",
  archived: "dark",
};

function formatStateLabel(state: ApplicationWorkflowState) {
  return state.replace("_", " ");
}

function formatDate(value: string | null) {
  if (!value) {
    return null;
  }
  return new Date(value).toLocaleDateString();
}

export function ApplicationsPage() {
  const [pipeline, setPipeline] = useState<ApplicationPipelineResponse | null>(null);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [transitioningId, setTransitioningId] = useState<string | null>(null);

  async function loadPipeline() {
    setLoading(true);
    setError(null);
    try {
      setPipeline(await getApplicationsPipeline({ includeInactive }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load applications");
    } finally {
      setLoading(false);
    }
  }

  async function moveApplication(
    application: ApplicationSummary,
    nextState: ApplicationWorkflowState,
  ) {
    setTransitioningId(application.id);
    setError(null);
    try {
      await transitionApplicationState(application.id, {
        state: nextState,
        reactivate: application.current_state === "archived",
      });
      await loadPipeline();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update application");
    } finally {
      setTransitioningId(null);
    }
  }

  useEffect(() => {
    void loadPipeline();
  }, [includeInactive]);

  const states = useMemo(
    () => (includeInactive ? ALL_STATES : ACTIVE_STATES),
    [includeInactive],
  );
  const hasApplications = states.some(
    (state) => (pipeline?.states[state] ?? []).length > 0,
  );

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={1}>Applications</Title>
          <Text c="dimmed">
            Application workflows grouped by their current pipeline state.
          </Text>
        </div>
        <Switch
          checked={includeInactive}
          label="Include archived"
          onChange={(event) => setIncludeInactive(event.currentTarget.checked)}
        />
      </Group>

      {loading ? <LoadingState label="Loading applications" /> : null}
      {!loading && error ? (
        <ErrorState message={error} onRetry={loadPipeline} />
      ) : null}

      {!loading && !error && !hasApplications ? (
        <Paper withBorder radius="md" p="lg">
          <Text c="dimmed">No application workflows yet.</Text>
        </Paper>
      ) : null}

      {!loading && !error && hasApplications ? (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
          {states.map((state) => (
            <Stack key={state} gap="sm">
              <Group justify="space-between">
                <Badge color={STATE_COLORS[state]} variant="filled">
                  {formatStateLabel(state)}
                </Badge>
                <Badge variant="default">
                  {pipeline?.states[state]?.length ?? 0}
                </Badge>
              </Group>

              {(pipeline?.states[state] ?? []).length === 0 ? (
                <Paper withBorder radius="md" p="md">
                  <Text c="dimmed" size="sm" ta="center">
                    No applications
                  </Text>
                </Paper>
              ) : null}

              {(pipeline?.states[state] ?? []).map((application) => (
                <ApplicationPipelineCard
                  key={application.id}
                  application={application}
                  transitioning={transitioningId === application.id}
                  onMove={moveApplication}
                />
              ))}
            </Stack>
          ))}
        </SimpleGrid>
      ) : null}
    </Stack>
  );
}

function ApplicationPipelineCard({
  application,
  transitioning,
  onMove,
}: {
  application: ApplicationSummary;
  transitioning: boolean;
  onMove: (
    application: ApplicationSummary,
    nextState: ApplicationWorkflowState,
  ) => void;
}) {
  const appliedDate = formatDate(application.applied_at);
  const nextActionDate = formatDate(application.next_action_at);

  return (
    <Card withBorder radius="md" p="md">
      <Stack gap="sm">
        <div>
          <Text
            component={Link}
            to={`/applications/${application.id}`}
            fw={600}
            lineClamp={2}
          >
            {application.title}
          </Text>
          <Text c="dimmed" size="sm">
            {application.company.name}
          </Text>
        </div>

        <Group gap="xs">
          <Badge color={STATE_COLORS[application.current_state]} variant="light">
            {formatStateLabel(application.current_state)}
          </Badge>
          <Text c="dimmed" size="xs">
            {application.counts.notes} notes
          </Text>
          <Text c="dimmed" size="xs">
            {application.counts.external_links} links
          </Text>
          <Text c="dimmed" size="xs">
            {application.counts.reminders} reminders
          </Text>
          <Text c="dimmed" size="xs">
            {application.counts.interviews} interviews
          </Text>
        </Group>

        {appliedDate || nextActionDate ? (
          <Stack gap={2}>
            {appliedDate ? (
              <Text size="xs" c="dimmed">
                Applied {appliedDate}
              </Text>
            ) : null}
            {nextActionDate ? (
              <Text size="xs" c="dimmed">
                Next action {nextActionDate}
              </Text>
            ) : null}
          </Stack>
        ) : null}

        {application.available_next_states.length > 0 ? (
          <Group gap="xs">
            {application.available_next_states.map((nextState) => (
              <Button
                key={nextState}
                size="xs"
                variant="outline"
                color={STATE_COLORS[nextState]}
                loading={transitioning}
                onClick={() => onMove(application, nextState)}
              >
                Move to {formatStateLabel(nextState)}
              </Button>
            ))}
          </Group>
        ) : null}
      </Stack>
    </Card>
  );
}
