import { Alert, Badge, Group, List, Paper, SimpleGrid, Stack, Text, Title } from "@mantine/core";
import { IconAlertTriangle } from "@tabler/icons-react";
import { useEffect, useState } from "react";

import { getProductizationReadiness } from "../api/productization";
import { ErrorState, LoadingState } from "./States";
import type { AiFeatureFlags, ProductizationReadiness } from "../types/productization";

function formatStatus(value: string) {
  return value.replaceAll("_", " ");
}

function enabledLabel(enabled: boolean) {
  return enabled ? "Enabled" : "Disabled";
}

function AiFeatureSummary({ flags }: { flags: AiFeatureFlags }) {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="xs">
      <Text size="sm">
        Opportunity parsing: {enabledLabel(flags.role_parsing_enabled)}
      </Text>
      <Text size="sm">COMPASS enrichment: {enabledLabel(flags.compass_enrichment_enabled)}</Text>
      <Text size="sm">Resume generation: {enabledLabel(flags.resume_generation_enabled)}</Text>
      <Text size="sm">
        Cover-letter generation: {enabledLabel(flags.cover_letter_generation_enabled)}
      </Text>
      <Text size="sm">
        Provider key configured: {flags.provider_key_configured ? "Yes" : "No"}
      </Text>
      <Text size="sm">
        Durable usage metering: {formatStatus(flags.durable_metering_status)}
      </Text>
    </SimpleGrid>
  );
}

export function ProductReadinessPanel() {
  const [readiness, setReadiness] = useState<ProductizationReadiness | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadReadiness() {
    setLoading(true);
    setError(null);
    try {
      setReadiness(await getProductizationReadiness());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load product readiness");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadReadiness();
  }, []);

  if (loading) {
    return <LoadingState label="Loading product readiness" />;
  }

  if (error && !readiness) {
    return <ErrorState message={error} onRetry={loadReadiness} />;
  }

  if (!readiness) {
    return null;
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>Product readiness</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Local-first deployment gate status for this Careero runtime.
            </Text>
          </div>
          <Badge color={readiness.production_ready ? "green" : "red"} variant="light">
            {readiness.production_ready ? "Production ready" : "Not production-ready"}
          </Badge>
        </Group>

        <Alert color="yellow" icon={<IconAlertTriangle size={18} />}>
          {readiness.production_readiness_statement}
        </Alert>

        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm">
          <div>
            <Text size="xs" c="dimmed">
              Environment
            </Text>
            <Text fw={600}>{readiness.environment}</Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              Readiness stage
            </Text>
            <Text fw={600}>{formatStatus(readiness.readiness_stage)}</Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              Local-first status
            </Text>
            <Text fw={600}>{formatStatus(readiness.local_first_status)}</Text>
          </div>
        </SimpleGrid>

        <Stack gap="xs">
          <Title order={4}>AI features</Title>
          <AiFeatureSummary flags={readiness.ai_feature_flags} />
        </Stack>

        <Stack gap="xs">
          <Title order={4}>Key blockers</Title>
          <List spacing="xs" size="sm">
            {readiness.known_blockers.slice(0, 6).map((blocker) => (
              <List.Item key={blocker}>{blocker}</List.Item>
            ))}
          </List>
        </Stack>
      </Stack>
    </Paper>
  );
}
