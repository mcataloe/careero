import { Badge, Button, Group, Paper, SimpleGrid, Stack, Text, Title } from "@mantine/core";
import { IconDownload, IconShieldLock } from "@tabler/icons-react";
import { useState } from "react";

import { exportAdvisorPacketMarkdown } from "../api/advisorPackets";
import type { AdvisorPacket } from "../types/advisorPackets";

interface AdvisorPacketPanelProps {
  applicationId: string;
  packet: AdvisorPacket;
}

export function AdvisorPacketPanel({ applicationId, packet }: AdvisorPacketPanelProps) {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const redactions = packet.redactions.slice(0, 6);

  async function handleExport() {
    setExporting(true);
    setError(null);
    try {
      await exportAdvisorPacketMarkdown(applicationId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not export packet");
    } finally {
      setExporting(false);
    }
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Group gap="xs">
            <Title order={3}>Advisor packet preview</Title>
            <Badge variant="light" leftSection={<IconShieldLock size={12} />}>
              Local only
            </Badge>
          </Group>
          <Text c="dimmed" size="sm" mt="xs">
            {packet.advisory_notice}
          </Text>
        </div>
        <Button
          leftSection={<IconDownload size={16} />}
          variant="light"
          loading={exporting}
          onClick={() => void handleExport()}
        >
          Export MD
        </Button>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm" mt="md">
        <PacketMetric label="State" value={packet.application.current_state} />
        <PacketMetric
          label="Artifacts"
          value={String(packet.artifacts.length)}
        />
        <PacketMetric
          label="External sharing"
          value={packet.external_sharing_enabled ? "Enabled" : "Disabled"}
        />
      </SimpleGrid>

      <Stack gap="sm" mt="md">
        <Text fw={600}>Redacted by default</Text>
        {redactions.map((redaction) => (
          <Group key={redaction.data_class} justify="space-between" align="flex-start">
            <div>
              <Text size="sm" fw={500}>
                {redaction.data_class}
              </Text>
              <Text size="xs" c="dimmed">
                {redaction.reason}
              </Text>
            </div>
            <Badge variant="outline" color={redaction.status === "excluded" ? "gray" : "blue"}>
              {redaction.status.replace("_", " ")}
            </Badge>
          </Group>
        ))}
      </Stack>

      <Stack gap="xs" mt="md">
        <Text fw={600}>Artifact summaries</Text>
        {packet.artifacts.length > 0 ? (
          packet.artifacts.map((artifact) => (
            <Text key={artifact.id} size="sm" c="dimmed">
              {artifact.title} - {artifact.lifecycle_status ?? "status unknown"} -
              content excluded
            </Text>
          ))
        ) : (
          <Text size="sm" c="dimmed">
            No generated resume or cover-letter artifacts found.
          </Text>
        )}
      </Stack>

      {error ? (
        <Text c="red" size="sm" mt="md">
          {error}
        </Text>
      ) : null}
    </Paper>
  );
}

function PacketMetric({ label, value }: { label: string; value: string }) {
  return (
    <Stack gap={0}>
      <Text size="xs" c="dimmed">
        {label}
      </Text>
      <Text fw={600}>{value}</Text>
    </Stack>
  );
}
