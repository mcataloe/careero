import { Alert, Badge, Button, Group, Stack, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import {
  archiveOpportunity,
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

      {notice ? <Alert color="green">{notice}</Alert> : null}
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

function isOpportunitySectionId(
  value: string | undefined,
): value is OpportunitySectionId {
  return typeof value === "string" && opportunitySectionIds.has(value);
}
