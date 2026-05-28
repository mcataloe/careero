import { Alert, Badge, Button, Card, Group, Stack, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import { ApiError } from "../api/client";
import {
  archiveOpportunity,
  ensureOpportunityApplication,
  getOpportunityApplication,
  getOpportunity,
  updateOpportunity,
} from "../api/opportunities";
import {
  createEvaluationWithStatus,
  getLatestEvaluation,
} from "../api/compassEvaluations";
import { CompassEvaluationDetail } from "../components/CompassEvaluationDetail";
import { FeatureWorkspaceLayout } from "../components/FeatureWorkspaceLayout";
import { RoleDetail } from "../components/RoleDetail";
import { ErrorState, LoadingState } from "../components/States";
import type {
  ApplicationDetail,
  ApplicationWorkflowState,
} from "../types/applications";
import type { CompassEvaluation } from "../types/compassEvaluations";
import type { Role, RoleUpdatePayload } from "../types/roles";

const opportunitySections = [
  {
    id: "overview",
    label: "Overview",
    description: "Core opportunity details",
  },
  {
    id: "intelligence",
    label: "Intelligence",
    description: "Stored caution and category signals",
  },
  {
    id: "description",
    label: "Description",
    description: "Raw and normalized posting text",
  },
  {
    id: "edit",
    label: "Edit",
    description: "Status and normalized fields",
  },
  {
    id: "compass",
    label: "COMPASS",
    description: "Evaluation and recommendations",
  },
] as const;

type OpportunitySectionId = (typeof opportunitySections)[number]["id"];
type RoleDetailSectionId = Exclude<OpportunitySectionId, "compass">;

const opportunitySectionIds = new Set<string>(
  opportunitySections.map((section) => section.id),
);

const APPLICATION_STATE_COLORS: Record<ApplicationWorkflowState, string> = {
  discovered: "gray",
  interested: "blue",
  applied: "teal",
  interviewing: "violet",
  offer: "green",
  rejected: "red",
  withdrawn: "orange",
  archived: "dark",
};

export function RoleDetailPage() {
  const { opportunityId, roleId, section } = useParams();
  const currentOpportunityId = opportunityId ?? roleId;
  const activeSection = isOpportunitySectionId(section) ? section : null;
  const navigate = useNavigate();
  const [role, setRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [evaluation, setEvaluation] = useState<CompassEvaluation | null>(null);
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [applicationLoading, setApplicationLoading] = useState(false);
  const [applicationCreating, setApplicationCreating] = useState(false);
  const [applicationError, setApplicationError] = useState<string | null>(null);
  const [evaluationLoading, setEvaluationLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadRole() {
    if (!currentOpportunityId) return;
    setLoading(true);
    setError(null);
    try {
      setRole(await getOpportunity(currentOpportunityId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load opportunity");
    } finally {
      setLoading(false);
    }
  }

  async function loadEvaluation() {
    if (!currentOpportunityId) return;
    setEvaluationLoading(true);
    setEvaluationError(null);
    try {
      setEvaluation(await getLatestEvaluation(currentOpportunityId));
    } catch (err) {
      setEvaluationError(
        err instanceof Error ? err.message : "Could not load evaluation",
      );
    } finally {
      setEvaluationLoading(false);
    }
  }

  async function loadApplicationWorkflow() {
    if (!currentOpportunityId || activeSection === "compass") return;
    setApplicationLoading(true);
    setApplicationError(null);
    try {
      setApplication(await getOpportunityApplication(currentOpportunityId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setApplication(null);
      } else {
        setApplicationError(
          err instanceof Error
            ? err.message
            : "Could not load application workflow",
        );
      }
    } finally {
      setApplicationLoading(false);
    }
  }

  async function handleTrackApplication() {
    if (!currentOpportunityId) return;
    setApplicationCreating(true);
    setApplicationError(null);
    setNotice(null);
    try {
      setApplication(await ensureOpportunityApplication(currentOpportunityId));
      setNotice("Application workflow started");
    } catch (err) {
      setApplicationError(
        err instanceof Error
          ? err.message
          : "Could not start application workflow",
      );
    } finally {
      setApplicationCreating(false);
    }
  }

  async function handleUpdate(payload: RoleUpdatePayload) {
    if (!currentOpportunityId) return;
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      setRole(await updateOpportunity(currentOpportunityId, payload));
      setNotice("Opportunity updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update opportunity");
    } finally {
      setSaving(false);
    }
  }

  async function handleArchive() {
    if (!currentOpportunityId) return;
    setArchiving(true);
    setError(null);
    try {
      await archiveOpportunity(currentOpportunityId);
      navigate("/opportunities");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not archive opportunity");
      setArchiving(false);
    }
  }

  async function handleRunEvaluation(force = false) {
    if (!currentOpportunityId) return;
    setEvaluating(true);
    setEvaluationError(null);
    setNotice(null);
    try {
      const result = await createEvaluationWithStatus(currentOpportunityId, {
        user_context: {},
        ...(force ? { force: true } : {}),
      });
      setEvaluation(result.evaluation);
      setNotice(
        result.status === 200
          ? "Cached COMPASS evaluation reused"
          : "COMPASS evaluation completed",
      );
      navigate(`/opportunities/${currentOpportunityId}/compass`);
    } catch (err) {
      setEvaluationError(
        err instanceof Error ? err.message : "Could not run evaluation",
      );
    } finally {
      setEvaluating(false);
    }
  }

  function viewLatestEvaluation() {
    if (currentOpportunityId) {
      navigate(`/opportunities/${currentOpportunityId}/compass`);
    }
  }

  useEffect(() => {
    void loadRole();
  }, [currentOpportunityId]);

  useEffect(() => {
    void loadApplicationWorkflow();
  }, [activeSection, currentOpportunityId]);

  useEffect(() => {
    if (activeSection === "compass") {
      void loadEvaluation();
    }
  }, [activeSection, currentOpportunityId]);

  if (!activeSection) {
    return (
      <Navigate to={`/opportunities/${currentOpportunityId ?? ""}/overview`} replace />
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Button component={Link} to="/opportunities" variant="subtle">
          Back to opportunities
        </Button>
      </Group>

      {notice ? (
        <Alert color="green" withCloseButton onClose={() => setNotice(null)}>
          {notice}
        </Alert>
      ) : null}
      {loading ? <LoadingState label="Loading opportunity" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadRole} /> : null}
      {!loading && !error && role ? (
        <>
          <Group justify="space-between" align="flex-start">
            <Stack gap={4}>
              <Title order={1}>{role.title}</Title>
              <Text c="dimmed">{role.company.name}</Text>
            </Stack>
            <Badge size="lg" variant="light">
              {role.status}
            </Badge>
          </Group>
          {activeSection !== "compass" ? (
            <OpportunityApplicationSummary
              application={application}
              loading={applicationLoading}
              creating={applicationCreating}
              error={applicationError}
              onRetry={loadApplicationWorkflow}
              onTrack={handleTrackApplication}
            />
          ) : null}
          <FeatureWorkspaceLayout
            navLabel="Opportunity sections"
            items={opportunitySections.map((item) => ({
              ...item,
              to: `/opportunities/${role.id}/${item.id}`,
            }))}
            activeId={activeSection}
            withDetailPanel={activeSection !== "compass"}
          >
            {activeSection === "compass" ? (
              <div id="compass-evaluation">
                {evaluationLoading ? <LoadingState label="Loading evaluation" /> : null}
                {!evaluationLoading && evaluationError ? (
                  <ErrorState message={evaluationError} onRetry={loadEvaluation} />
                ) : null}
                {!evaluationLoading && !evaluationError ? (
                  <CompassEvaluationDetail
                    evaluation={evaluation}
                    onRun={handleRunEvaluation}
                    running={evaluating}
                    onViewLatest={viewLatestEvaluation}
                  />
                ) : null}
              </div>
            ) : (
              <RoleDetail
                role={role}
                onUpdate={handleUpdate}
                onArchive={handleArchive}
                saving={saving}
                archiving={archiving}
                activeSection={activeSection as RoleDetailSectionId}
              />
            )}
          </FeatureWorkspaceLayout>
        </>
      ) : null}
    </Stack>
  );
}

function OpportunityApplicationSummary({
  application,
  loading,
  creating,
  error,
  onRetry,
  onTrack,
}: {
  application: ApplicationDetail | null;
  loading: boolean;
  creating: boolean;
  error: string | null;
  onRetry: () => void;
  onTrack: () => void;
}) {
  if (loading) {
    return <LoadingState label="Loading application workflow" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={onRetry} />;
  }

  if (!application) {
    return (
      <Card withBorder radius="md" p="md">
        <Group justify="space-between" align="flex-start">
          <Stack gap={4}>
            <Text fw={600}>Application workflow</Text>
            <Text c="dimmed" size="sm">
              Not tracked as an application yet.
            </Text>
          </Stack>
          <Button size="xs" variant="light" loading={creating} onClick={onTrack}>
            Track as application
          </Button>
        </Group>
      </Card>
    );
  }

  return (
    <Card withBorder radius="md" p="md">
      <Group justify="space-between" align="flex-start">
        <Stack gap={4}>
          <Text fw={600}>Application workflow</Text>
          <Text c="dimmed" size="sm">
            Search track: {application.workspace.title}
          </Text>
        </Stack>
        <Badge color={APPLICATION_STATE_COLORS[application.current_state]} variant="light">
          {application.current_state}
        </Badge>
      </Group>
      <Group gap="sm" mt="sm">
        <Text size="sm" c="dimmed">
          Notes {application.counts.notes} - Reminders{" "}
          {application.counts.reminders} - Interviews{" "}
          {application.counts.interviews}
        </Text>
        <Button
          component={Link}
          to={`/applications/${application.id}/overview`}
          size="xs"
          variant="light"
        >
          Open application
        </Button>
      </Group>
    </Card>
  );
}

function isOpportunitySectionId(
  value: string | undefined,
): value is OpportunitySectionId {
  return typeof value === "string" && opportunitySectionIds.has(value);
}
