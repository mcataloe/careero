import { Alert, Button, Group, Stack } from "@mantine/core";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  archiveOpportunity,
  getOpportunity,
  updateOpportunity,
} from "../api/opportunities";
import {
  createEvaluationWithStatus,
  getLatestEvaluation,
} from "../api/compassEvaluations";
import { RoleDetail } from "../components/RoleDetail";
import { SectionNavigation } from "../components/SectionNavigation";
import { CompassEvaluationDetail } from "../components/CompassEvaluationDetail";
import { ErrorState, LoadingState } from "../components/States";
import type { Role, RoleUpdatePayload } from "../types/roles";
import type { CompassEvaluation } from "../types/compassEvaluations";

export function RoleDetailPage() {
  const { opportunityId, roleId } = useParams();
  const currentOpportunityId = opportunityId ?? roleId;
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
  const evaluationRef = useRef<HTMLDivElement | null>(null);
  const evaluationSectionNavItems = evaluation
    ? [
        { label: "Summary", targetId: "compass-summary" },
        { label: "Fit Analysis", targetId: "compass-fit-analysis" },
        { label: "Strengths", targetId: "compass-strengths" },
        { label: "Gaps", targetId: "compass-gaps" },
        { label: "Risks", targetId: "compass-risks" },
        { label: "ATS Findings", targetId: "compass-ats-findings" },
        { label: "Compensation", targetId: "compass-compensation" },
        { label: "Remote Fit", targetId: "compass-remote-fit" },
        { label: "Interview Positioning", targetId: "compass-interview-positioning" },
        { label: "Recommendations", targetId: "compass-recommendations" },
        { label: "Assumptions / Confidence", targetId: "compass-assumptions-confidence" },
      ]
    : [];
  const sectionNavItems = [
    { label: "Overview", targetId: "role-overview" },
    { label: "Opportunity Intelligence", targetId: "opportunity-intelligence" },
    { label: "Description", targetId: "role-description" },
    { label: "Normalized Description", targetId: "role-normalized-description" },
    { label: "Edit Opportunity", targetId: "role-edit" },
    { label: "COMPASS Evaluation", targetId: "compass-evaluation" },
    ...evaluationSectionNavItems,
  ];

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
      const nextEvaluation = result.evaluation;
      setEvaluation(nextEvaluation);
      setNotice(
        result.status === 200
          ? "Cached COMPASS evaluation reused"
          : "COMPASS evaluation completed",
      );
      evaluationRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      setEvaluationError(
        err instanceof Error ? err.message : "Could not run evaluation",
      );
    } finally {
      setEvaluating(false);
    }
  }

  function viewLatestEvaluation() {
    evaluationRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  useEffect(() => {
    void loadRole();
    void loadEvaluation();
  }, [currentOpportunityId]);

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
          <RoleDetail
            role={role}
            onUpdate={handleUpdate}
            onArchive={handleArchive}
            saving={saving}
            archiving={archiving}
            sectionNav={<SectionNavigation items={sectionNavItems} />}
          />
          <div id="compass-evaluation" ref={evaluationRef}>
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
        </>
      ) : null}
    </Stack>
  );
}
