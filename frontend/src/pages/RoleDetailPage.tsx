import { Alert, Button, Group, Stack } from "@mantine/core";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { archiveRole, getRole, updateRole } from "../api/roles";
import { createEvaluation, getLatestEvaluation } from "../api/strideEvaluations";
import { RoleDetail } from "../components/RoleDetail";
import { StrideEvaluationDetail } from "../components/StrideEvaluationDetail";
import { ErrorState, LoadingState } from "../components/States";
import type { Role, RoleUpdatePayload } from "../types/roles";
import type { StrideEvaluation } from "../types/strideEvaluations";

export function RoleDetailPage() {
  const { roleId } = useParams();
  const navigate = useNavigate();
  const [role, setRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [evaluation, setEvaluation] = useState<StrideEvaluation | null>(null);
  const [evaluationLoading, setEvaluationLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const evaluationRef = useRef<HTMLDivElement | null>(null);

  async function loadRole() {
    if (!roleId) return;
    setLoading(true);
    setError(null);
    try {
      setRole(await getRole(roleId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load role");
    } finally {
      setLoading(false);
    }
  }

  async function loadEvaluation() {
    if (!roleId) return;
    setEvaluationLoading(true);
    setEvaluationError(null);
    try {
      setEvaluation(await getLatestEvaluation(roleId));
    } catch (err) {
      setEvaluationError(
        err instanceof Error ? err.message : "Could not load evaluation",
      );
    } finally {
      setEvaluationLoading(false);
    }
  }

  async function handleUpdate(payload: RoleUpdatePayload) {
    if (!roleId) return;
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      setRole(await updateRole(roleId, payload));
      setNotice("Role updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update role");
    } finally {
      setSaving(false);
    }
  }

  async function handleArchive() {
    if (!roleId) return;
    setArchiving(true);
    setError(null);
    try {
      await archiveRole(roleId);
      navigate("/roles");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not archive role");
      setArchiving(false);
    }
  }

  async function handleRunEvaluation() {
    if (!roleId) return;
    setEvaluating(true);
    setEvaluationError(null);
    setNotice(null);
    try {
      const nextEvaluation = await createEvaluation(roleId, {
        user_context: {},
      });
      setEvaluation(nextEvaluation);
      setNotice("STRIDE evaluation completed");
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
  }, [roleId]);

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Button component={Link} to="/roles" variant="subtle">
          Back to roles
        </Button>
      </Group>

      {notice ? <Alert color="green">{notice}</Alert> : null}
      {loading ? <LoadingState label="Loading role" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadRole} /> : null}
      {!loading && !error && role ? (
        <>
          <RoleDetail
            role={role}
            onUpdate={handleUpdate}
            onArchive={handleArchive}
            saving={saving}
            archiving={archiving}
          />
          <div ref={evaluationRef}>
            {evaluationLoading ? <LoadingState label="Loading evaluation" /> : null}
            {!evaluationLoading && evaluationError ? (
              <ErrorState message={evaluationError} onRetry={loadEvaluation} />
            ) : null}
            {!evaluationLoading && !evaluationError ? (
              <StrideEvaluationDetail
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
