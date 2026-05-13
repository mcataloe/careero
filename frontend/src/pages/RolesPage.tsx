import { Button, Group, Stack, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listRoles } from "../api/roles";
import { RolesList } from "../components/RolesList";
import { ErrorState, LoadingState } from "../components/States";
import type { Role } from "../types/roles";

export function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadRoles() {
    setLoading(true);
    setError(null);
    try {
      setRoles(await listRoles());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load roles");
    } finally {
      setLoading(false);
    }
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
      {!loading && !error ? <RolesList roles={roles} /> : null}
    </Stack>
  );
}
