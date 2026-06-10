import { Alert, Paper, Stack, Text, Title } from "@mantine/core";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createOpportunity } from "../api/opportunities";
import { RoleForm } from "../components/RoleForm";
import type { OpportunityCreatePayload } from "../types/opportunities";

export function RoleNewPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(payload: OpportunityCreatePayload) {
    setSubmitting(true);
    setError(null);
    try {
      const opportunity = await createOpportunity(payload);
      navigate(`/opportunities/${opportunity.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create opportunity");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Add opportunity</Title>
        <Text c="dimmed">
          Paste details from LinkedIn, a company site, or another manual source.
        </Text>
      </div>

      {error ? (
        <Alert color="red" title="Opportunity was not created">
          {error}
        </Alert>
      ) : null}

      <Paper withBorder radius="md" p="lg">
        <RoleForm onSubmit={handleSubmit} submitting={submitting} />
      </Paper>
    </Stack>
  );
}
