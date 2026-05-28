import {
  Alert,
  Badge,
  Button,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Switch,
  Text,
  TextInput,
  Textarea,
  Title,
} from "@mantine/core";
import {
  IconArchive,
  IconCheck,
  IconCopyPlus,
  IconDeviceFloppy,
  IconFileText,
  IconSend,
} from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";

import {
  archiveArtifact,
  markArtifactReviewed,
  markArtifactSubmitted,
  updateArtifactDraft,
} from "../api/artifacts";
import type { ArtifactLifecycleStatus, ArtifactRecord } from "../types/artifacts";
import type { ApplicationDetail } from "../types/applications";

const STATUS_COLORS: Record<ArtifactLifecycleStatus, string> = {
  draft: "gray",
  reviewed: "blue",
  submitted: "green",
  archived: "dark",
};

export function ApplicationArtifactsPanel({
  application,
  artifacts,
  includeArchived,
  onIncludeArchivedChange,
  onChanged,
}: {
  application: ApplicationDetail;
  artifacts: ArtifactRecord[];
  includeArchived: boolean;
  onIncludeArchivedChange: (value: boolean) => void;
  onChanged: () => Promise<void>;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [workingId, setWorkingId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  const selectedArtifact = useMemo(
    () => artifacts.find((artifact) => artifact.id === selectedId) ?? artifacts[0],
    [artifacts, selectedId],
  );
  const resumeArtifacts = artifacts.filter(
    (artifact) => artifact.artifact_type === "tailored_resume",
  );
  const coverLetterArtifacts = artifacts.filter(
    (artifact) => artifact.artifact_type === "cover_letter",
  );
  const submittedArtifacts = artifacts.filter(
    (artifact) => artifact.lifecycle_status === "submitted",
  );

  useEffect(() => {
    if (selectedId === null && artifacts.length > 0) {
      setSelectedId(artifacts[0].id);
    }
    if (selectedArtifact && !artifacts.some((artifact) => artifact.id === selectedArtifact.id)) {
      setSelectedId(artifacts[0]?.id ?? null);
    }
  }, [artifacts, selectedArtifact, selectedId]);

  async function runAction(
    artifact: ArtifactRecord,
    action: () => Promise<ArtifactRecord>,
    message: string,
  ) {
    setWorkingId(artifact.id);
    setNotice(null);
    setError(null);
    try {
      const nextArtifact = await action();
      setSelectedId(nextArtifact.id);
      setNotice(message);
      setEditing(false);
      await onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Artifact action failed");
    } finally {
      setWorkingId(null);
    }
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <Stack gap={4}>
          <Title order={2}>Artifacts</Title>
          <Text c="dimmed" size="sm">
            {application.company.name} - {application.workspace.title}
          </Text>
        </Stack>
        <Switch
          checked={includeArchived}
          onChange={(event) => onIncludeArchivedChange(event.currentTarget.checked)}
          label="Show archived"
        />
      </Group>

      {notice ? (
        <Alert
          color="green"
          withCloseButton
          closeButtonLabel="Dismiss notification"
          onClose={() => setNotice(null)}
        >
          {notice}
        </Alert>
      ) : null}
      {error ? (
        <Alert
          color="red"
          withCloseButton
          closeButtonLabel="Dismiss error"
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      ) : null}

      {artifacts.length === 0 ? (
        <Paper withBorder radius="md" p="lg">
          <Stack gap={4}>
            <Text fw={600}>No artifacts yet</Text>
            <Text c="dimmed" size="sm">
              Generate or create a resume draft or cover-letter draft for this
              opportunity before review and submitted tracking can begin.
            </Text>
          </Stack>
        </Paper>
      ) : (
        <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="md">
          <ArtifactColumn
            title="Resume artifacts"
            artifacts={resumeArtifacts}
            selectedId={selectedArtifact?.id ?? null}
            workingId={workingId}
            onSelect={setSelectedId}
            onReview={(artifact) =>
              runAction(
                artifact,
                () => markArtifactReviewed(artifact.id),
                "Artifact marked reviewed.",
              )
            }
            onSubmit={(artifact) =>
              runAction(
                artifact,
                () => markArtifactSubmitted(artifact.id),
                "Artifact marked submitted.",
              )
            }
            onArchive={(artifact) =>
              runAction(
                artifact,
                () => archiveArtifact(artifact.id),
                "Artifact archived.",
              )
            }
          />
          <ArtifactColumn
            title="Cover-letter artifacts"
            artifacts={coverLetterArtifacts}
            selectedId={selectedArtifact?.id ?? null}
            workingId={workingId}
            onSelect={setSelectedId}
            onReview={(artifact) =>
              runAction(
                artifact,
                () => markArtifactReviewed(artifact.id),
                "Artifact marked reviewed.",
              )
            }
            onSubmit={(artifact) =>
              runAction(
                artifact,
                () => markArtifactSubmitted(artifact.id),
                "Artifact marked submitted.",
              )
            }
            onArchive={(artifact) =>
              runAction(
                artifact,
                () => archiveArtifact(artifact.id),
                "Artifact archived.",
              )
            }
          />
        </SimpleGrid>
      )}

      {submittedArtifacts.length > 0 ? (
        <Paper withBorder radius="md" p="md">
          <Text fw={600}>Submitted versions</Text>
          <Group gap="xs" mt="xs">
            {submittedArtifacts.map((artifact) => (
              <Badge key={artifact.id} color="green" variant="light">
                {artifactLabel(artifact)} v{artifact.version_number}
              </Badge>
            ))}
          </Group>
        </Paper>
      ) : null}

      {selectedArtifact ? (
        <ArtifactDetail
          artifact={selectedArtifact}
          editing={editing}
          working={workingId === selectedArtifact.id}
          onEditChange={setEditing}
          onCreateRevision={(artifact) =>
            runAction(
              artifact,
              () =>
                updateArtifactDraft(artifact.id, {
                  title: artifact.title,
                  content: artifact.content,
                  change_summary: "Created a new draft from submitted artifact.",
                }),
              "New draft version created.",
            )
          }
          onChanged={onChanged}
        />
      ) : null}
    </Stack>
  );
}

function ArtifactColumn({
  title,
  artifacts,
  selectedId,
  workingId,
  onSelect,
  onReview,
  onSubmit,
  onArchive,
}: {
  title: string;
  artifacts: ArtifactRecord[];
  selectedId: string | null;
  workingId: string | null;
  onSelect: (artifactId: string) => void;
  onReview: (artifact: ArtifactRecord) => void;
  onSubmit: (artifact: ArtifactRecord) => void;
  onArchive: (artifact: ArtifactRecord) => void;
}) {
  return (
    <Stack gap="sm">
      <Text fw={600}>{title}</Text>
      {artifacts.length === 0 ? (
        <Paper withBorder radius="md" p="md">
          <Text size="sm" c="dimmed">
            None yet.
          </Text>
        </Paper>
      ) : (
        artifacts.map((artifact) => (
          <Paper
            key={artifact.id}
            withBorder
            radius="md"
            p="md"
            bg={artifact.id === selectedId ? "var(--mantine-color-blue-0)" : undefined}
          >
            <Stack gap="sm">
              <Group justify="space-between" align="flex-start">
                <Stack gap={2}>
                  <Text fw={600}>{artifact.title}</Text>
                  <Text size="xs" c="dimmed">
                    Version {artifact.version_number} - Updated{" "}
                    {formatDate(artifact.updated_at)}
                  </Text>
                </Stack>
                <Badge
                  color={STATUS_COLORS[artifact.lifecycle_status]}
                  variant="light"
                >
                  {formatStatus(artifact.lifecycle_status)}
                </Badge>
              </Group>
              <Group gap="xs">
                <Button
                  size="xs"
                  variant="light"
                  leftSection={<IconFileText size={14} />}
                  onClick={() => onSelect(artifact.id)}
                >
                  View
                </Button>
                {artifact.available_transitions.includes("reviewed") ? (
                  <Button
                    size="xs"
                    variant="outline"
                    leftSection={<IconCheck size={14} />}
                    loading={workingId === artifact.id}
                    onClick={() => onReview(artifact)}
                  >
                    Review
                  </Button>
                ) : null}
                {artifact.available_transitions.includes("submitted") ? (
                  <Button
                    size="xs"
                    variant="outline"
                    color="green"
                    leftSection={<IconSend size={14} />}
                    loading={workingId === artifact.id}
                    onClick={() => onSubmit(artifact)}
                  >
                    Submit
                  </Button>
                ) : null}
                {artifact.available_transitions.includes("archived") ? (
                  <Button
                    size="xs"
                    variant="subtle"
                    color="red"
                    leftSection={<IconArchive size={14} />}
                    loading={workingId === artifact.id}
                    onClick={() => onArchive(artifact)}
                  >
                    Archive
                  </Button>
                ) : null}
              </Group>
            </Stack>
          </Paper>
        ))
      )}
    </Stack>
  );
}

function ArtifactDetail({
  artifact,
  editing,
  working,
  onEditChange,
  onCreateRevision,
  onChanged,
}: {
  artifact: ArtifactRecord;
  editing: boolean;
  working: boolean;
  onEditChange: (editing: boolean) => void;
  onCreateRevision: (artifact: ArtifactRecord) => void;
  onChanged: () => Promise<void>;
}) {
  const [draftTitle, setDraftTitle] = useState(artifact.title);
  const [draftContent, setDraftContent] = useState(artifact.content);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setDraftTitle(artifact.title);
    setDraftContent(artifact.content);
    setSaveError(null);
    onEditChange(false);
  }, [artifact.id]);

  async function saveDraft() {
    setSaveError(null);
    setSaving(true);
    try {
      await updateArtifactDraft(artifact.id, {
        title: draftTitle,
        content: draftContent,
        change_summary: "Saved draft artifact edits.",
      });
      onEditChange(false);
      await onChanged();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Could not save artifact");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <Stack gap={2}>
            <Title order={3}>{artifact.title}</Title>
            <Text c="dimmed" size="sm">
              {artifactLabel(artifact)} - Version {artifact.version_number}
            </Text>
          </Stack>
          <Badge color={STATUS_COLORS[artifact.lifecycle_status]} variant="filled">
            {formatStatus(artifact.lifecycle_status)}
          </Badge>
        </Group>

        {artifact.lifecycle_status === "submitted" ? (
          <Alert color="green" title="Submitted version">
            This exact artifact version is preserved as submitted. Further edits
            create a new draft version.
          </Alert>
        ) : null}
        {artifact.lifecycle_status === "archived" ? (
          <Alert color="gray" title="Archived artifact">
            Archived artifacts stay available for history and are hidden from
            active lists by default.
          </Alert>
        ) : null}
        {saveError ? (
          <Alert color="red" title="Could not save draft">
            {saveError}
          </Alert>
        ) : null}

        <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="sm">
          <TraceLabel label="Search track" value={artifact.traceability.workspace_id} />
          <TraceLabel label="Opportunity" value={artifact.traceability.opportunity_id} />
          <TraceLabel label="Evaluation" value={artifact.traceability.evaluation_id} />
          <TraceLabel label="Source artifact" value={artifact.traceability.source_artifact_id} />
        </SimpleGrid>

        <Group gap="xs">
          {artifact.reviewed_at ? (
            <Badge variant="outline">Reviewed {formatDate(artifact.reviewed_at)}</Badge>
          ) : null}
          {artifact.submitted_at ? (
            <Badge color="green" variant="outline">
              Submitted {formatDate(artifact.submitted_at)}
            </Badge>
          ) : null}
          {artifact.archived_at ? (
            <Badge color="dark" variant="outline">
              Archived {formatDate(artifact.archived_at)}
            </Badge>
          ) : null}
          {artifact.traceability.export_formats.map((format) => (
            <Badge key={format} color="gray" variant="light">
              {format.toUpperCase()}
            </Badge>
          ))}
        </Group>

        {artifact.lifecycle_status === "draft" && editing ? (
          <Stack gap="sm">
            <TextInput
              label="Title"
              value={draftTitle}
              onChange={(event) => setDraftTitle(event.currentTarget.value)}
            />
            <Textarea
              label="Employer-facing content"
              minRows={12}
              autosize
              value={draftContent}
              onChange={(event) => setDraftContent(event.currentTarget.value)}
            />
            <Group gap="xs">
              <Button
                size="sm"
                leftSection={<IconDeviceFloppy size={16} />}
                loading={working || saving}
                onClick={saveDraft}
              >
                Save draft
              </Button>
              <Button
                size="sm"
                variant="subtle"
                onClick={() => onEditChange(false)}
              >
                Cancel
              </Button>
            </Group>
          </Stack>
        ) : (
          <Paper withBorder radius="md" p="md">
            <Text size="xs" c="dimmed" mb="xs">
              Employer-facing content
            </Text>
            <Text style={{ whiteSpace: "pre-wrap" }}>{artifact.content}</Text>
          </Paper>
        )}

        <Group gap="xs">
          {artifact.lifecycle_status === "draft" && !editing ? (
            <Button
              size="sm"
              variant="light"
              leftSection={<IconFileText size={16} />}
              onClick={() => onEditChange(true)}
            >
              Edit draft
            </Button>
          ) : null}
          {artifact.lifecycle_status === "submitted" ? (
            <Button
              size="sm"
              variant="light"
              leftSection={<IconCopyPlus size={16} />}
              loading={working}
              onClick={() => onCreateRevision(artifact)}
            >
              New draft
            </Button>
          ) : null}
        </Group>
      </Stack>
    </Paper>
  );
}

function TraceLabel({ label, value }: { label: string; value: string | null }) {
  return (
    <Paper withBorder radius="md" p="sm">
      <Text size="xs" c="dimmed">
        {label}
      </Text>
      <Text size="xs">{value ?? "Not linked"}</Text>
    </Paper>
  );
}

function artifactLabel(artifact: ArtifactRecord) {
  return artifact.artifact_type === "cover_letter" ? "Cover letter" : "Resume";
}

function formatStatus(status: ArtifactLifecycleStatus) {
  return status.replaceAll("_", " ");
}

function formatDate(value: string | null) {
  if (!value) {
    return "Not set";
  }
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
