import {
  Badge,
  Button,
  Group,
  NumberInput,
  Paper,
  Stack,
  Switch,
  Text,
  Title,
} from "@mantine/core";
import { useEffect, useState } from "react";

import {
  getAutomationPreferences,
  updateAutomationPreferences,
} from "../api/automation";
import { listWorkspaces } from "../api/workspaces";
import { ErrorState, LoadingState } from "./States";
import type {
  AutomationPreferences,
  AutomationPreferencesPayload,
} from "../types/automation";
import type { Workspace } from "../types/workspaces";

export function AutomationPreferencesPanel() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [preferences, setPreferences] = useState<AutomationPreferences | null>(null);
  const [draft, setDraft] = useState<AutomationPreferencesPayload>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPreferences() {
    setLoading(true);
    setError(null);
    try {
      const workspaces = await listWorkspaces();
      const activeWorkspace = workspaces.find((item) => item.status === "active") ?? workspaces[0];
      if (!activeWorkspace) {
        setWorkspace(null);
        setPreferences(null);
        return;
      }
      const nextPreferences = await getAutomationPreferences(activeWorkspace.id);
      setWorkspace(activeWorkspace);
      setPreferences(nextPreferences);
      setDraft({
        enabled: nextPreferences.enabled,
        follow_up_suggestion_days: nextPreferences.follow_up_suggestion_days,
        artifact_readiness_checks_enabled:
          nextPreferences.artifact_readiness_checks_enabled,
        communication_drafts_enabled: nextPreferences.communication_drafts_enabled,
        internal_state_change_suggestions_enabled:
          nextPreferences.internal_state_change_suggestions_enabled,
        quiet_mode: nextPreferences.quiet_mode,
        future_external_actions_enabled: false,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load automation settings");
    } finally {
      setLoading(false);
    }
  }

  async function savePreferences() {
    if (!workspace) return;
    setSaving(true);
    setError(null);
    try {
      const nextPreferences = await updateAutomationPreferences(workspace.id, {
        ...draft,
        future_external_actions_enabled: false,
      });
      setPreferences(nextPreferences);
      setDraft({
        enabled: nextPreferences.enabled,
        follow_up_suggestion_days: nextPreferences.follow_up_suggestion_days,
        artifact_readiness_checks_enabled:
          nextPreferences.artifact_readiness_checks_enabled,
        communication_drafts_enabled: nextPreferences.communication_drafts_enabled,
        internal_state_change_suggestions_enabled:
          nextPreferences.internal_state_change_suggestions_enabled,
        quiet_mode: nextPreferences.quiet_mode,
        future_external_actions_enabled: false,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save automation settings");
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadPreferences();
  }, []);

  if (loading) {
    return <LoadingState label="Loading automation settings" />;
  }

  if (error && !preferences) {
    return <ErrorState message={error} onRetry={loadPreferences} />;
  }

  if (!workspace || !preferences) {
    return (
      <Paper withBorder radius="md" p="lg">
        <Text c="dimmed" size="sm">
          Create a workspace before configuring automation settings.
        </Text>
      </Paper>
    );
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>Automation guardrails</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Workspace defaults for local suggestions and approval logging.
            </Text>
          </div>
          <Badge variant="light">External actions disabled</Badge>
        </Group>
        {error ? (
          <Text c="red" size="sm">
            {error}
          </Text>
        ) : null}
        <Text size="sm" c="dimmed">
          Workspace: {workspace.title}
        </Text>
        <Switch
          label="Enable local suggestions"
          checked={draft.enabled ?? preferences.enabled}
          onChange={(event) =>
            setDraft((current) => ({
              ...current,
              enabled: event.currentTarget.checked,
            }))
          }
        />
        <NumberInput
          label="Follow-up suggestion threshold"
          min={1}
          max={90}
          value={
            draft.follow_up_suggestion_days ??
            preferences.follow_up_suggestion_days
          }
          onChange={(value) =>
            setDraft((current) => ({
              ...current,
              follow_up_suggestion_days: Number(value) || 7,
            }))
          }
        />
        <Switch
          label="Artifact readiness checks"
          checked={
            draft.artifact_readiness_checks_enabled ??
            preferences.artifact_readiness_checks_enabled
          }
          onChange={(event) =>
            setDraft((current) => ({
              ...current,
              artifact_readiness_checks_enabled: event.currentTarget.checked,
            }))
          }
        />
        <Switch
          label="Communication drafts stay local"
          checked={
            draft.communication_drafts_enabled ??
            preferences.communication_drafts_enabled
          }
          onChange={(event) =>
            setDraft((current) => ({
              ...current,
              communication_drafts_enabled: event.currentTarget.checked,
            }))
          }
        />
        <Switch
          label="Internal state-change suggestions"
          checked={
            draft.internal_state_change_suggestions_enabled ??
            preferences.internal_state_change_suggestions_enabled
          }
          onChange={(event) =>
            setDraft((current) => ({
              ...current,
              internal_state_change_suggestions_enabled:
                event.currentTarget.checked,
            }))
          }
        />
        <Switch
          label="Quiet mode"
          checked={draft.quiet_mode ?? preferences.quiet_mode}
          onChange={(event) =>
            setDraft((current) => ({
              ...current,
              quiet_mode: event.currentTarget.checked,
            }))
          }
        />
        <Switch
          label="Future external actions"
          checked={false}
          disabled
          description="Not available in this local MVP."
        />
        <Group>
          <Button loading={saving} onClick={() => void savePreferences()}>
            Save settings
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}
