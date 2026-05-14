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

const MAX_IMPORT_FILE_BYTES = 5 * 1024 * 1024;
const IMPORT_ACCEPT = ".txt,.md,.docx,.pdf";

export function ResumeSourceSettings() {
  const [activeSource, setActiveSource] = useState<ActiveResumeSource | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [importing, setImporting] = useState(false);
  const [inputMode, setInputMode] = useState<"paste" | "upload">("paste");
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

  async function loadActiveSource() {
    setLoading(true);
    setError(null);
    try {
      const active = await getActiveResumeSource();
      setActiveSource(active);
      if (active) {
        form.setValues({
          name: active.source.name,
          versionLabel: "",
          rawText: active.version.raw_text,
          normalizedSummary: active.version.normalized_summary ?? "",
        });
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load resume source",
      );
    } finally {
      setLoading(false);
    }
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
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap="lg">
          <Group justify="space-between" align="flex-start">
            <Stack gap={4}>
              <Title order={3}>Resume/profile source</Title>
              <Text c="dimmed">
                Active local grounding source for STRIDE evaluation.
              </Text>
            </Stack>
            {activeSource ? (
              <Text size="sm" c="dimmed">
                Active version: {activeSource.version.version_label}
              </Text>
            ) : null}
          </Group>

          {!activeSource ? (
            <EmptyState
              title="No active source"
              message="Paste a master resume or profile so evaluations can compare roles against your actual background."
            />
          ) : (
            <Alert color="green" title="Active source configured">
              {activeSource.source.name} is active for STRIDE grounding.
            </Alert>
          )}

          {notice ? <Alert color="green">{notice}</Alert> : null}
          {error ? (
            <ErrorState message={error} onRetry={loadActiveSource} />
          ) : null}
          {importError ? <Alert color="red">{importError}</Alert> : null}

          <Stack gap="sm">
            <SegmentedControl
              value={inputMode}
              onChange={(value) => setInputMode(value as "paste" | "upload")}
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
                    Upload .txt, .md, .docx, or text-based .pdf files up to 5
                    MB. Uploading extracts text only; it does not save the
                    source.
                  </Text>
                </Stack>
                <Group>
                  <FileButton
                    onChange={handleImport}
                  accept={IMPORT_ACCEPT}
                  disabled={importing}
                  >
                    {(props) => (
                      <Button
                        {...props}
                        type="button"
                        variant="light"
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
                        Characters:{" "}
                        {importResult.character_count.toLocaleString()}
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
                Paste resume or profile text directly into the raw text field
                below.
              </Text>
            )}
          </Stack>

          <Grid>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <TextInput label="Source name" {...form.getInputProps("name")} />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <TextInput
                label={activeSource ? "New version label" : "Version label"}
                placeholder={activeSource ? "v2" : "v1"}
                {...form.getInputProps("versionLabel")}
              />
            </Grid.Col>
            <Grid.Col span={12}>
              <Textarea
                label="Raw resume/profile text"
                minRows={8}
                autosize
                {...form.getInputProps("rawText")}
              />
            </Grid.Col>
            <Grid.Col span={12}>
              <Textarea
                label="Normalized summary"
                minRows={3}
                autosize
                {...form.getInputProps("normalizedSummary")}
              />
            </Grid.Col>
          </Grid>

          <Group justify="flex-end">
            <Button type="submit" loading={saving}>
              {activeSource ? "Save active version" : "Create active source"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Paper>
  );
}
