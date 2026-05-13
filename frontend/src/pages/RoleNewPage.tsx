import { Alert, Paper, Stack, Text, Title } from "@mantine/core";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createRole } from "../api/roles";
import { RoleForm } from "../components/RoleForm";
import type { RoleCreatePayload } from "../types/roles";

export function RoleNewPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(payload: RoleCreatePayload) {
    setSubmitting(true);
    setError(null);
    try {
      const role = await createRole(payload);
      navigate(`/roles/${role.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create role");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Add role</Title>
        <Text c="dimmed">
          Paste details from LinkedIn, a company site, or another manual source.
        </Text>
      </div>

      {error ? (
        <Alert color="red" title="Role was not created">
          {error}
        </Alert>
      ) : null}

      <Paper withBorder radius="md" p="lg">
        <RoleForm onSubmit={handleSubmit} submitting={submitting} />
      </Paper>
    </Stack>
  );
}
