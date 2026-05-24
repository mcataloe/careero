import { Badge, Button, Group, Paper, Stack, Text, Title } from "@mantine/core";
import { useState } from "react";

import {
  approveAutomationSuggestion,
  dismissAutomationSuggestion,
  rejectAutomationSuggestion,
} from "../api/automation";
import type { AutomationSuggestion } from "../types/automation";

interface AutomationSuggestionsPanelProps {
  suggestions: AutomationSuggestion[];
  title?: string;
  onChanged: () => Promise<void> | void;
}

export function AutomationSuggestionsPanel({
  suggestions,
  title = "Reviewable suggestions",
  onChanged,
}: AutomationSuggestionsPanelProps) {
  const [pendingId, setPendingId] = useState<string | null>(null);
  const visibleSuggestions = suggestions.slice(0, 8);

  async function handleDecision(
    suggestion: AutomationSuggestion,
    decision: "approve" | "dismiss" | "reject",
  ) {
    setPendingId(suggestion.id);
    try {
      if (decision === "approve") {
        await approveAutomationSuggestion(suggestion.id);
      } else if (decision === "reject") {
        await rejectAutomationSuggestion(suggestion.id);
      } else {
        await dismissAutomationSuggestion(suggestion.id);
      }
      await onChanged();
    } finally {
      setPendingId(null);
    }
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={3}>{title}</Title>
          <Text c="dimmed" size="sm" mt="xs">
            Local suggestions with visible reasons and no external action.
          </Text>
        </div>
        <Badge variant="light">External actions disabled</Badge>
      </Group>

      <Stack gap="md" mt="md">
        {visibleSuggestions.length > 0 ? (
          visibleSuggestions.map((suggestion) => (
            <Paper key={suggestion.id} withBorder radius="sm" p="md">
              <Stack gap="xs">
                <Group justify="space-between" align="flex-start">
                  <div>
                    <Text fw={600}>{suggestion.title}</Text>
                    <Text size="sm" c="dimmed">
                      {formatAction(suggestion.action_type)} - {suggestion.confidence}
                    </Text>
                  </div>
                  <Badge variant="light">{suggestion.status}</Badge>
                </Group>
                <Text size="sm">{suggestion.summary}</Text>
                <Text size="sm" c="dimmed">
                  {suggestion.reason}
                </Text>
                <Text size="xs" c="dimmed">
                  {suggestion.basis}
                </Text>
                <Paper bg="gray.0" radius="sm" p="sm">
                  <Text size="sm" fw={600}>
                    {suggestion.preview.title}
                  </Text>
                  <Text size="sm">{suggestion.preview.body}</Text>
                  {suggestion.action_type === "communication_draft" ? (
                    <Text size="xs" c="dimmed" mt={4}>
                      Draft only. Careero will not send this message.
                    </Text>
                  ) : null}
                </Paper>
                {suggestion.status === "active" ? (
                  <Group gap="xs">
                    <Button
                      size="xs"
                      variant="light"
                      loading={pendingId === suggestion.id}
                      onClick={() => void handleDecision(suggestion, "approve")}
                    >
                      Approve log
                    </Button>
                    <Button
                      size="xs"
                      variant="subtle"
                      color="gray"
                      loading={pendingId === suggestion.id}
                      onClick={() => void handleDecision(suggestion, "dismiss")}
                    >
                      Dismiss
                    </Button>
                    <Button
                      size="xs"
                      variant="subtle"
                      color="red"
                      loading={pendingId === suggestion.id}
                      onClick={() => void handleDecision(suggestion, "reject")}
                    >
                      Reject
                    </Button>
                  </Group>
                ) : null}
              </Stack>
            </Paper>
          ))
        ) : (
          <Text c="dimmed" size="sm">
            No reviewable suggestions are active.
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

function formatAction(action: string) {
  return action.replaceAll("_", " ");
}
