import {
  Alert,
  Button,
  FileButton,
  Grid,
  Group,
  Paper,
  SegmentedControl,
  Stack,
  Text,
  TextInput,
  Textarea,
  Title,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useEffect, useState } from "react";

import {
  activateResumeSourceVersion,
  createResumeSource,
  createResumeSourceVersion,
  getActiveResumeSource,
  importResumeSourceFile,
} from "../api/resumeSources";
import type {
  ActiveResumeSource,
  ResumeSourceImportResponse,
} from "../types/resumeSources";
import { EmptyState, ErrorState, LoadingState } from "./States";
import { MarkdownPreviewBlock } from "./MarkdownPreviewBlock";
import { ReadOnlyField } from "./ReadOnlyField";

const MAX_IMPORT_FILE_BYTES = 5 * 1024 * 1024;
const IMPORT_ACCEPT = ".txt,.md,.docx,.pdf";

type InputMode = "paste" | "upload";
type TextMode = "edit" | "preview";

export function ResumeSourceSettings() {
  const [activeSource, setActiveSource] = useState<ActiveResumeSource | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [importing, setImporting] = useState(false);
  const [editingDraft, setEditingDraft] = useState(false);
  const [inputMode, setInputMode] = useState<InputMode>("paste");
  const [textMode, setTextMode] = useState<TextMode>("edit");
  const [importResult, setImportResult] =
    useState<ResumeSourceImportResponse | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const form = useForm({
    initialValues: {
      name: "Master Resume",
      versionLabel: "v1",
      rawText: "",
      normalizedSummary: "",
    },
    validate: {
      name: (value) => (value.trim() ? null : "Name is required"),
      versionLabel: (value) =>
        value.trim() ? null : "Version label is required",
      rawText: (value) => (value.trim() ? null : "Source text is required"),
    },
  });

  function resetDraftFromActive(active: ActiveResumeSource | null) {
    form.setValues({
      name: active?.source.name ?? "Master Resume",
      versionLabel: active ? "" : "v1",
      rawText: active?.version.raw_text ?? "",
      normalizedSummary: active?.version.normalized_summary ?? "",
    });
  }

  function clearImportState() {
    setImportResult(null);
    setImportError(null);
  }

  async function loadActiveSource() {
    setLoading(true);
    setError(null);
    try {
      const active = await getActiveResumeSource();
      setActiveSource(active);
      resetDraftFromActive(active);
      setEditingDraft(!active);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load resume source",
      );
    } finally {
      setLoading(false);
    }
  }

  function startDraft(mode: InputMode = "paste") {
    resetDraftFromActive(activeSource);
    clearImportState();
    setNotice(null);
    setInputMode(mode);
    setTextMode("edit");
    setEditingDraft(true);
  }

  function cancelDraft() {
    resetDraftFromActive(activeSource);
    clearImportState();
    setNotice(null);
    setTextMode("edit");
    setInputMode("paste");
    setEditingDraft(!activeSource);
  }

  async function handleImport(file: File | null) {
    setImportResult(null);
    setImportError(null);
    setNotice(null);

    if (!file) {
      return;
    }

    if (file.size > MAX_IMPORT_FILE_BYTES) {
      setImportError("Resume/profile file must be 5 MB or smaller.");
      return;
    }

    setEditingDraft(true);
    setInputMode("upload");
    setTextMode("edit");
    setImporting(true);
    try {
      const result = await importResumeSourceFile(file);
      form.setFieldValue("rawText", result.extracted_text);
      setImportResult(result);
      setNotice(
        "Resume/profile text extracted. Review and edit before saving.",
      );
    } catch (err) {
      setImportError(
        err instanceof Error ? err.message : "Could not import file",
      );
    } finally {
      setImporting(false);
    }
  }

  async function handleSubmit(values: typeof form.values) {
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      if (!activeSource) {
        await createResumeSource({
          name: values.name.trim(),
          source_type: "master_resume",
          version_label: values.versionLabel.trim(),
          raw_text: values.rawText.trim(),
          normalized_summary: values.normalizedSummary.trim() || null,
          is_active: true,
        });
        setNotice("Active resume source created");
      } else {
        const version = await createResumeSourceVersion(
          activeSource.source.id,
          {
            version_label: values.versionLabel.trim(),
            raw_text: values.rawText.trim(),
            normalized_summary: values.normalizedSummary.trim() || null,
            is_active: false,
          },
        );
        await activateResumeSourceVersion(activeSource.source.id, version.id);
        setNotice("Active resume source updated");
      }
      clearImportState();
      await loadActiveSource();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not save resume source",
      );
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadActiveSource();
  }, []);

  if (loading) {
    return <LoadingState label="Loading resume source" />;
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="lg">
        <Group justify="space-between" align="flex-start">
          <Stack gap={4}>
            <Title order={3}>Resume/profile source</Title>
            <Text c="dimmed">
              Active local grounding source for STRIDE evaluation.
            </Text>
          </Stack>
          {activeSource && !editingDraft ? (
            <Text size="sm" c="dimmed">
              Active version: {activeSource.version.version_label}
            </Text>
          ) : null}
        </Group>

        {notice ? <Alert color="green">{notice}</Alert> : null}
        {error ? <ErrorState message={error} onRetry={loadActiveSource} /> : null}
        {importError ? <Alert color="red">{importError}</Alert> : null}

        {activeSource && !editingDraft ? (
          <ActiveSourcePreview
            activeSource={activeSource}
            onCreateVersion={() => startDraft("paste")}
            onImport={() => startDraft("upload")}
          />
        ) : (
          <form noValidate onSubmit={form.onSubmit(handleSubmit)}>
            <Stack gap="lg">
              {!activeSource ? (
                <EmptyState
                  title="No active source"
                  message="Paste a master resume or profile so evaluations can compare roles against your actual background."
                />
              ) : (
                <Alert color="blue" title="Draft version">
                  Review changes carefully. Saving creates and activates a new
                  source version.
                </Alert>
              )}

              <DraftInputControls
                inputMode={inputMode}
                setInputMode={setInputMode}
                importing={importing}
                importResult={importResult}
                onImport={handleImport}
              />

              <Grid>
                <Grid.Col span={{ base: 12, md: 6 }}>
                  <TextInput
                    label="Source name"
                    {...form.getInputProps("name")}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 12, md: 6 }}>
                  <TextInput
                    label={activeSource ? "New version label" : "Version label"}
                    placeholder={activeSource ? "v2" : "v1"}
                    required
                    {...form.getInputProps("versionLabel")}
                  />
                </Grid.Col>
              </Grid>

              <Stack gap="sm">
                <Group justify="space-between" align="center">
                  <Text fw={600}>Source text</Text>
                  <SegmentedControl
                    size="xs"
                    value={textMode}
                    onChange={(value) => setTextMode(value as TextMode)}
                    data={[
                      { label: "Edit", value: "edit" },
                      { label: "Preview", value: "preview" },
                    ]}
                  />
                </Group>

                {textMode === "preview" ? (
                  <Stack>
                    <ReadOnlyField label="Raw resume/profile text" long>
                      <MarkdownPreviewBlock value={form.values.rawText} />
                    </ReadOnlyField>
                    <ReadOnlyField label="Normalized summary" long maxHeight={220}>
                      <MarkdownPreviewBlock
                        value={form.values.normalizedSummary}
                        empty="No normalized summary recorded."
                      />
                    </ReadOnlyField>
                  </Stack>
                ) : (
                  <Grid>
                    <Grid.Col span={12}>
                      <Textarea
                        label="Raw resume/profile text"
                        minRows={8}
                        maxRows={16}
                        autosize
                        {...form.getInputProps("rawText")}
                      />
                    </Grid.Col>
                    <Grid.Col span={12}>
                      <Textarea
                        label="Normalized summary"
                        minRows={3}
                        maxRows={10}
                        autosize
                        {...form.getInputProps("normalizedSummary")}
                      />
                    </Grid.Col>
                  </Grid>
                )}
              </Stack>

              <Group justify="flex-end">
                {activeSource ? (
                  <Button type="button" variant="default" onClick={cancelDraft}>
                    Cancel
                  </Button>
                ) : null}
                <Button type="submit" loading={saving}>
                  {activeSource ? "Save active version" : "Create active source"}
                </Button>
              </Group>
            </Stack>
          </form>
        )}
      </Stack>
    </Paper>
  );
}

function ActiveSourcePreview({
  activeSource,
  onCreateVersion,
  onImport,
}: {
  activeSource: ActiveResumeSource;
  onCreateVersion: () => void;
  onImport: () => void;
}) {
  return (
    <Stack gap="lg">
      <Alert color="green" title="Active source configured">
        {activeSource.source.name} is active for STRIDE grounding.
      </Alert>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReadOnlyField label="Source name" value={activeSource.source.name} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReadOnlyField
            label="Active version"
            value={activeSource.version.version_label}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReadOnlyField
            label="Source updated"
            value={formatDateTime(activeSource.source.updated_at)}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReadOnlyField
            label="Version updated"
            value={formatDateTime(activeSource.version.updated_at)}
          />
        </Grid.Col>
      </Grid>

      <ReadOnlyField label="Raw resume/profile text" long maxHeight={320}>
        <MarkdownPreviewBlock value={activeSource.version.raw_text} />
      </ReadOnlyField>

      <ReadOnlyField label="Normalized summary" long maxHeight={240}>
        <MarkdownPreviewBlock
          value={activeSource.version.normalized_summary}
          empty="No normalized summary recorded."
        />
      </ReadOnlyField>

      <Group justify="flex-end">
        <Button type="button" variant="outline" onClick={onImport}>
          Import file
        </Button>
        <Button type="button" onClick={onCreateVersion}>
          Create new version
        </Button>
      </Group>
    </Stack>
  );
}

function DraftInputControls({
  inputMode,
  setInputMode,
  importing,
  importResult,
  onImport,
}: {
  inputMode: InputMode;
  setInputMode: (mode: InputMode) => void;
  importing: boolean;
  importResult: ResumeSourceImportResponse | null;
  onImport: (file: File | null) => void;
}) {
  return (
    <Stack gap="sm">
      <SegmentedControl
        value={inputMode}
        onChange={(value) => setInputMode(value as InputMode)}
        data={[
          { label: "Paste text", value: "paste" },
          { label: "Upload file", value: "upload" },
        ]}
      />
      {inputMode === "upload" ? (
        <Stack gap="xs">
          <Stack gap={4}>
            <Text fw={500}>Resume/profile file</Text>
            <Text size="sm" c="dimmed">
              Upload .txt, .md, .docx, or text-based .pdf files up to 5 MB.
              Uploading extracts text only; it does not save the source.
            </Text>
          </Stack>
          <Group>
            <FileButton
              onChange={onImport}
              accept={IMPORT_ACCEPT}
              disabled={importing}
            >
              {(props) => (
                <Button
                  {...props}
                  type="button"
                  variant="outline"
                  loading={importing}
                >
                  Choose file to import
                </Button>
              )}
            </FileButton>
          </Group>
          {importing ? <Text size="sm">Extracting text...</Text> : null}
          {importResult ? (
            <Alert color="blue" title="Imported file">
              <Stack gap={4}>
                <Text size="sm">File: {importResult.file_name}</Text>
                <Text size="sm">Type: {importResult.file_type}</Text>
                <Text size="sm">
                  Characters: {importResult.character_count.toLocaleString()}
                </Text>
                {importResult.warnings.map((warning) => (
                  <Text key={warning} size="sm">
                    Warning: {warning}
                  </Text>
                ))}
              </Stack>
            </Alert>
          ) : null}
        </Stack>
      ) : (
        <Text size="sm" c="dimmed">
          Paste resume or profile text directly into the raw text field below.
        </Text>
      )}
    </Stack>
  );
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return null;
  return new Date(value).toLocaleString();
}
