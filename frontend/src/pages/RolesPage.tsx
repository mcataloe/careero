import { Button, Group, Stack, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listRoles } from "../api/roles";
import { getLatestEvaluation } from "../api/strideEvaluations";
import { RolesList } from "../components/RolesList";
import { ErrorState, LoadingState } from "../components/States";
import type { Role } from "../types/roles";
import type { EvaluationSummaryState } from "../types/strideEvaluations";

export function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [evaluationStates, setEvaluationStates] = useState<
    Record<string, EvaluationSummaryState>
  >({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadRoles() {
    setLoading(true);
    setError(null);
    try {
      const nextRoles = await listRoles();
      setRoles(nextRoles);
      setEvaluationStates(
        Object.fromEntries(nextRoles.map((role) => [role.id, { status: "loading" }])),
      );
      void loadEvaluationIndicators(nextRoles);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load roles");
    } finally {
      setLoading(false);
    }
  }

  async function loadEvaluationIndicators(nextRoles: Role[]) {
    await Promise.all(
      nextRoles.map(async (role) => {
        try {
          const evaluation = await getLatestEvaluation(role.id);
          setEvaluationStates((current) => ({
            ...current,
            [role.id]: evaluation
              ? { status: "completed", evaluation }
              : { status: "not_evaluated" },
          }));
        } catch (err) {
          setEvaluationStates((current) => ({
            ...current,
            [role.id]: {
              status: "error",
              message: err instanceof Error ? err.message : "Could not load evaluation",
            },
          }));
        }
      }),
    );
  }

  useEffect(() => {
    void loadRoles();
  }, []);

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={1}>Roles</Title>
          <Text c="dimmed">Roles found manually and queued for later evaluation.</Text>
        </div>
        <Button component={Link} to="/roles/new">
          Add role
        </Button>
      </Group>

      {loading ? <LoadingState label="Loading roles" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadRoles} /> : null}
      {!loading && !error ? (
        <RolesList roles={roles} evaluationStates={evaluationStates} />
      ) : null}
    </Stack>
  );
}
