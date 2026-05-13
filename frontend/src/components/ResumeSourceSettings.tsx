import {
  Alert,
  Button,
  Grid,
  Group,
  Paper,
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
} from "../api/resumeSources";
import type { ActiveResumeSource } from "../types/resumeSources";
import { EmptyState, ErrorState, LoadingState } from "./States";

export function ResumeSourceSettings() {
  const [activeSource, setActiveSource] = useState<ActiveResumeSource | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
      versionLabel: (value) => (value.trim() ? null : "Version label is required"),
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
      setError(err instanceof Error ? err.message : "Could not load resume source");
    } finally {
      setLoading(false);
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
        const version = await createResumeSourceVersion(activeSource.source.id, {
          version_label: values.versionLabel.trim(),
          raw_text: values.rawText.trim(),
          normalized_summary: values.normalizedSummary.trim() || null,
          is_active: false,
        });
        await activateResumeSourceVersion(activeSource.source.id, version.id);
        setNotice("Active resume source updated");
      }
      await loadActiveSource();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save resume source");
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
          {error ? <ErrorState message={error} onRetry={loadActiveSource} /> : null}

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
