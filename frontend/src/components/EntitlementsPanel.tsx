import { Alert, Badge, Group, List, Paper, SimpleGrid, Stack, Text, Title } from "@mantine/core";
import { IconCircleCheck, IconCreditCardOff } from "@tabler/icons-react";
import { useEffect, useState } from "react";

import { getCurrentEntitlements } from "../api/entitlements";
import { ErrorState, LoadingState } from "./States";
import type { CurrentEntitlements } from "../types/entitlements";

function formatValue(value: string) {
  return value.replaceAll("_", " ");
}

export function EntitlementsPanel() {
  const [entitlements, setEntitlements] = useState<CurrentEntitlements | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadEntitlements() {
    setLoading(true);
    setError(null);
    try {
      setEntitlements(await getCurrentEntitlements());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load entitlements");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadEntitlements();
  }, []);

  if (loading) {
    return <LoadingState label="Loading entitlements" />;
  }

  if (error && !entitlements) {
    return <ErrorState message={error} onRetry={loadEntitlements} />;
  }

  if (!entitlements) {
    return null;
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>Local plan</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Current local entitlement boundary without payments or checkout.
            </Text>
          </div>
          <Badge leftSection={<IconCreditCardOff size={14} />} variant="light">
            Billing not configured
          </Badge>
        </Group>

        <Alert color="blue">{entitlements.local_first_note}</Alert>

        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm">
          <div>
            <Text size="xs" c="dimmed">
              Plan
            </Text>
            <Text fw={600}>{entitlements.plan_display_name}</Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              Billing
            </Text>
            <Text fw={600}>{formatValue(entitlements.billing_status)}</Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              Payment provider
            </Text>
            <Text fw={600}>{formatValue(entitlements.payment_provider)}</Text>
          </div>
        </SimpleGrid>

        <Stack gap="xs">
          <Title order={4}>Included locally</Title>
          <List spacing="xs" size="sm" icon={<IconCircleCheck size={16} />}>
            {entitlements.entitlements
              .filter((item) => item.enabled)
              .slice(0, 7)
              .map((item) => (
                <List.Item key={item.key}>{item.description}</List.Item>
              ))}
          </List>
        </Stack>

        <Stack gap="xs">
          <Title order={4}>Future only</Title>
          <Text size="sm">
            {entitlements.unavailable_future_features
              .slice(0, 6)
              .map(formatValue)
              .join(", ")}
          </Text>
        </Stack>
      </Stack>
    </Paper>
  );
}
