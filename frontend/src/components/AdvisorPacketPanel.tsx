import {
  Badge,
  Button,
  Checkbox,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Textarea,
  Title,
} from "@mantine/core";
import { IconDownload, IconRefresh, IconShieldLock } from "@tabler/icons-react";
import { useState } from "react";

import { exportAdvisorPacketMarkdown } from "../api/advisorPackets";
import type {
  ApplicationExternalLink,
  ApplicationInterviewStage,
} from "../types/applications";
import type {
  AdvisorPacket,
  AdvisorPacketPreviewOptions,
  AdvisorPacketWarning,
} from "../types/advisorPackets";

interface AdvisorPacketPanelProps {
  applicationId: string;
  packet: AdvisorPacket;
  externalLinks: ApplicationExternalLink[];
  interviews: ApplicationInterviewStage[];
  onRefresh: (options: AdvisorPacketPreviewOptions) => Promise<void>;
}

export function AdvisorPacketPanel({
  applicationId,
  packet,
  externalLinks,
  interviews,
  onRefresh,
}: AdvisorPacketPanelProps) {
  const [selectedArtifactIds, setSelectedArtifactIds] = useState<string[]>([]);
  const [selectedExternalLinkIds, setSelectedExternalLinkIds] = useState<string[]>([]);
  const [selectedInterviewIds, setSelectedInterviewIds] = useState<string[]>([]);
  const [advisorContext, setAdvisorContext] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const previewOptions: AdvisorPacketPreviewOptions = {
    artifactIds: selectedArtifactIds,
    externalLinkIds: selectedExternalLinkIds,
    interviewStageIds: selectedInterviewIds,
    advisorContext,
  };

  async function handleRefresh() {
    setRefreshing(true);
    setError(null);
    try {
      await onRefresh(previewOptions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not refresh packet");
    } finally {
      setRefreshing(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    setError(null);
    try {
      await exportAdvisorPacketMarkdown(applicationId, previewOptions);
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
            <Title order={3}>Advisor Packet Preview</Title>
            <Badge variant="light" leftSection={<IconShieldLock size={12} />}>
              Local only
            </Badge>
          </Group>
          <Text c="dimmed" size="sm" mt="xs">
            Local preview only. Nothing is shared externally.
          </Text>
          <Text c="dimmed" size="sm">
            {packet.advisory_notice}
          </Text>
        </div>
        <Group gap="xs">
          <Button
            leftSection={<IconRefresh size={16} />}
            variant="light"
            loading={refreshing}
            onClick={() => void handleRefresh()}
          >
            Refresh preview
          </Button>
          <Button
            leftSection={<IconDownload size={16} />}
            variant="outline"
            loading={exporting}
            onClick={() => void handleExport()}
          >
            Export Markdown
          </Button>
        </Group>
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
        <Text fw={600}>Optional local preview includes</Text>
        {packet.artifacts.length > 0 ? (
          packet.artifacts.map((artifact) => (
            <Checkbox
              key={artifact.id}
              checked={selectedArtifactIds.includes(artifact.id)}
              label={`Include artifact content: ${artifact.title}`}
              description="Explicit local preview selection; lifecycle and TruthGuard warnings remain attached."
              onChange={(event) =>
                setSelectedArtifactIds((current) =>
                  toggleId(current, artifact.id, event.currentTarget.checked),
                )
              }
            />
          ))
        ) : null}
        {externalLinks.map((link) => (
          <Checkbox
            key={link.id}
            checked={selectedExternalLinkIds.includes(link.id)}
            label={`Include link: ${link.label}`}
            description="Review links for private portals or tracking URLs before including."
            onChange={(event) =>
              setSelectedExternalLinkIds((current) =>
                toggleId(current, link.id, event.currentTarget.checked),
              )
            }
          />
        ))}
        {interviews.map((interview) => (
          <Checkbox
            key={interview.id}
            checked={selectedInterviewIds.includes(interview.id)}
            label={`Include interview notes: ${interview.title}`}
            description="Interviewer names and meeting links stay redacted."
            onChange={(event) =>
              setSelectedInterviewIds((current) =>
                toggleId(current, interview.id, event.currentTarget.checked),
              )
            }
          />
        ))}
        <Textarea
          label="Advisor context"
          value={advisorContext}
          minRows={2}
          maxLength={4000}
          onChange={(event) => setAdvisorContext(event.currentTarget.value)}
        />
      </Stack>

      <Stack gap="xs" mt="md">
        <Text fw={600}>Included sections</Text>
        {packet.sections
          .filter((section) => section.status !== "excluded")
          .map((section) => (
            <Group key={section.key} justify="space-between" align="flex-start">
              <Text size="sm">{section.title}</Text>
              <Badge variant="light">
                {section.status.replace("_", " ")} - {section.item_count}
              </Badge>
            </Group>
          ))}
      </Stack>

      <Stack gap="sm" mt="md">
        <Text fw={600}>Redacted by default</Text>
        {packet.redactions.map((redaction) => (
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
            <Stack key={artifact.id} gap={2}>
              <Text size="sm" c="dimmed">
                {artifact.title} - {artifact.lifecycle_status ?? "status unknown"} -
                content {artifact.content_included ? "included" : "excluded"}
              </Text>
              <WarningList warnings={artifact.warnings} />
              {artifact.content_included && artifact.content ? (
                <Paper withBorder p="sm" radius="sm">
                  <Text size="sm" style={{ whiteSpace: "pre-wrap" }}>
                    {artifact.content}
                  </Text>
                </Paper>
              ) : null}
            </Stack>
          ))
        ) : (
          <Text size="sm" c="dimmed">
            No generated resume or cover-letter artifacts found.
          </Text>
        )}
      </Stack>

      {packet.selected_external_links.length > 0 ? (
        <Stack gap="xs" mt="md">
          <Text fw={600}>Selected links</Text>
          {packet.selected_external_links.map((link) => (
            <Text key={link.id} size="sm" c="dimmed">
              {link.label} - {link.url}
            </Text>
          ))}
        </Stack>
      ) : null}

      {packet.selected_interviews.length > 0 ? (
        <Stack gap="xs" mt="md">
          <Text fw={600}>Selected interview notes</Text>
          {packet.selected_interviews.map((interview) => (
            <Text key={interview.id} size="sm" c="dimmed">
              {interview.title} - notes included
            </Text>
          ))}
        </Stack>
      ) : null}

      {packet.advisor_context ? (
        <Stack gap="xs" mt="md">
          <Text fw={600}>Advisor context</Text>
          <Text size="sm" c="dimmed">
            {packet.advisor_context}
          </Text>
        </Stack>
      ) : null}

      <Stack gap="xs" mt="md">
        <Text fw={600}>Warnings</Text>
        <WarningList warnings={packet.warnings} />
      </Stack>

      {error ? (
        <Text c="red" size="sm" mt="md">
          {error}
        </Text>
      ) : null}
    </Paper>
  );
}

function toggleId(current: string[], id: string, checked: boolean) {
  if (checked) {
    return current.includes(id) ? current : [...current, id];
  }
  return current.filter((currentId) => currentId !== id);
}

function WarningList({ warnings }: { warnings: AdvisorPacketWarning[] }) {
  if (!warnings.length) {
    return (
      <Text size="sm" c="dimmed">
        No warnings.
      </Text>
    );
  }

  return (
    <Stack gap={2}>
      {warnings.map((warning) => (
        <Text key={warning.code} size="xs" c="dimmed">
          {warning.message}
        </Text>
      ))}
    </Stack>
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
