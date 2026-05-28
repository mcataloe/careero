import {
  Badge,
  Button,
  Card,
  Group,
  Stack,
  Text,
  Textarea,
  TextInput,
} from "@mantine/core";
import { useState } from "react";

import {
  completeApplicationReminder,
  createApplicationReminder,
  updateApplicationReminder,
} from "../api/applications";
import type {
  ApplicationReminder,
  ApplicationReminderPayload,
} from "../types/applications";

interface ReminderDraft {
  title: string;
  dueAt: string;
  notes: string;
}

const emptyDraft: ReminderDraft = {
  title: "",
  dueAt: "",
  notes: "",
};

function toApiDatetime(value: string) {
  return new Date(value).toISOString();
}

function toLocalInputValue(value: string) {
  const date = new Date(value);
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function reminderStatus(reminder: ApplicationReminder) {
  if (reminder.completed_at) {
    return { label: "Complete", color: "green" };
  }
  const due = new Date(reminder.due_at);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
  if (due < now) {
    return { label: "Overdue", color: "red" };
  }
  if (due >= today && due < tomorrow) {
    return { label: "Due today", color: "orange" };
  }
  return { label: "Upcoming", color: "blue" };
}

export function ApplicationRemindersPanel({
  applicationId,
  reminders,
  onChanged,
}: {
  applicationId: string;
  reminders: ApplicationReminder[];
  onChanged: () => Promise<void>;
}) {
  const [draft, setDraft] = useState<ReminderDraft>(emptyDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<ReminderDraft>(emptyDraft);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCreate = Boolean(draft.title.trim() && draft.dueAt);
  const canEdit = Boolean(editDraft.title.trim() && editDraft.dueAt);

  async function submitCreate() {
    if (!canCreate) {
      return;
    }
    await runMutation(async () => {
      await createApplicationReminder(applicationId, {
        title: draft.title.trim(),
        due_at: toApiDatetime(draft.dueAt),
        notes: draft.notes.trim() || null,
      });
      setDraft(emptyDraft);
    });
  }

  function startEdit(reminder: ApplicationReminder) {
    setEditingId(reminder.id);
    setEditDraft({
      title: reminder.title,
      dueAt: toLocalInputValue(reminder.due_at),
      notes: reminder.notes ?? "",
    });
    setError(null);
  }

  async function submitEdit(reminderId: string) {
    if (!canEdit) {
      return;
    }
    const payload: ApplicationReminderPayload = {
      title: editDraft.title.trim(),
      due_at: toApiDatetime(editDraft.dueAt),
      notes: editDraft.notes.trim() || null,
    };
    await runMutation(async () => {
      await updateApplicationReminder(applicationId, reminderId, payload);
      setEditingId(null);
    });
  }

  async function completeReminder(reminderId: string) {
    await runMutation(async () => {
      await completeApplicationReminder(applicationId, reminderId);
      if (editingId === reminderId) {
        setEditingId(null);
      }
    });
  }

  async function runMutation(mutation: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await mutation();
      await onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update reminders");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <div>
          <Text fw={600}>Reminders</Text>
          <Text size="sm" c="dimmed">
            Track local follow-ups and due dates for this application.
          </Text>
        </div>

        <Stack gap="sm">
          <Group align="end" grow>
            <TextInput
              label="Reminder title"
              placeholder="Follow up with recruiter"
              value={draft.title}
              onChange={(event) => {
                const value = event.currentTarget.value;
                setDraft((current) => ({
                  ...current,
                  title: value,
                }));
              }}
            />
            <TextInput
              label="Due date"
              type="datetime-local"
              value={draft.dueAt}
              onChange={(event) => {
                const value = event.currentTarget.value;
                setDraft((current) => ({
                  ...current,
                  dueAt: value,
                }));
              }}
            />
          </Group>
          <Textarea
            label="Reminder notes"
            placeholder="Optional context"
            value={draft.notes}
            onChange={(event) => {
              const value = event.currentTarget.value;
              setDraft((current) => ({
                ...current,
                notes: value,
              }));
            }}
            autosize
            minRows={2}
            maxRows={5}
          />
          <Group justify="flex-end">
            <Button onClick={submitCreate} loading={busy} disabled={!canCreate}>
              Add reminder
            </Button>
          </Group>
        </Stack>

        {error ? (
          <Text c="red" size="sm" role="alert">
            {error}
          </Text>
        ) : null}

        {reminders.length === 0 ? (
          <Card withBorder radius="sm" p="md">
            <Text c="dimmed" size="sm">
              No reminders yet. Add the next follow-up date when this application
              needs attention.
            </Text>
          </Card>
        ) : (
          <Stack gap="sm">
            {reminders.map((reminder) => (
              <Card key={reminder.id} withBorder radius="sm" p="md">
                {editingId === reminder.id ? (
                  <Stack gap="sm">
                    <Group align="end" grow>
                      <TextInput
                        label="Edit reminder title"
                        value={editDraft.title}
                        onChange={(event) => {
                          const value = event.currentTarget.value;
                          setEditDraft((current) => ({
                            ...current,
                            title: value,
                          }));
                        }}
                      />
                      <TextInput
                        label="Edit due date"
                        type="datetime-local"
                        value={editDraft.dueAt}
                        onChange={(event) => {
                          const value = event.currentTarget.value;
                          setEditDraft((current) => ({
                            ...current,
                            dueAt: value,
                          }));
                        }}
                      />
                    </Group>
                    <Textarea
                      label="Edit reminder notes"
                      value={editDraft.notes}
                      onChange={(event) => {
                        const value = event.currentTarget.value;
                        setEditDraft((current) => ({
                          ...current,
                          notes: value,
                        }));
                      }}
                      autosize
                      minRows={2}
                      maxRows={5}
                    />
                    <Group justify="flex-end" gap="xs">
                      <Button
                        variant="default"
                        onClick={() => setEditingId(null)}
                        disabled={busy}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={() => submitEdit(reminder.id)}
                        loading={busy}
                        disabled={!canEdit}
                      >
                        Save reminder
                      </Button>
                    </Group>
                  </Stack>
                ) : (
                  <Group justify="space-between" align="flex-start">
                    <div>
                      <Group gap="xs">
                        <Text fw={600}>{reminder.title}</Text>
                        <Badge
                          color={reminderStatus(reminder).color}
                          variant="light"
                        >
                          {reminderStatus(reminder).label}
                        </Badge>
                      </Group>
                      <Text size="sm" c="dimmed">
                        Due {formatDateTime(reminder.due_at)}
                      </Text>
                      {reminder.completed_at ? (
                        <Text size="xs" c="dimmed">
                          Completed {formatDateTime(reminder.completed_at)}
                        </Text>
                      ) : null}
                      {reminder.notes ? (
                        <Text size="sm" mt={4} style={{ whiteSpace: "pre-wrap" }}>
                          {reminder.notes}
                        </Text>
                      ) : null}
                    </div>
                    <Group gap="xs">
                      <Button
                        size="xs"
                        variant="default"
                        onClick={() => startEdit(reminder)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="xs"
                        variant="outline"
                        onClick={() => completeReminder(reminder.id)}
                        loading={busy}
                        disabled={Boolean(reminder.completed_at)}
                      >
                        Complete
                      </Button>
                    </Group>
                  </Group>
                )}
              </Card>
            ))}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
