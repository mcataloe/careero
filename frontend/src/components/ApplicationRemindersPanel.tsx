import {
  Badge,
  Button,
  Card,
  Group,
  Select,
  Stack,
  Text,
  TextInput,
  Textarea,
} from "@mantine/core";
import { useState } from "react";

import {
  completeApplicationReminder,
  createApplicationReminder,
  deleteApplicationReminder,
  reopenApplicationReminder,
} from "../api/applications";
import type {
  ApplicationReminder,
  ApplicationReminderPriority,
  ApplicationReminderType,
} from "../types/applications";

const TYPE_OPTIONS: { value: ApplicationReminderType; label: string }[] = [
  { value: "follow_up", label: "Follow up" },
  { value: "deadline", label: "Deadline" },
  { value: "next_action", label: "Next action" },
  { value: "interview_prep", label: "Interview prep" },
  { value: "thank_you", label: "Thank-you note" },
  { value: "status_check", label: "Status check" },
  { value: "revisit", label: "Revisit" },
  { value: "submit_application", label: "Submit application" },
  { value: "other", label: "Other" },
];

const PRIORITY_OPTIONS: { value: ApplicationReminderPriority; label: string }[] = [
  { value: "normal", label: "Normal" },
  { value: "high", label: "High" },
  { value: "low", label: "Low" },
];

function toLocalInputValue(date = new Date(Date.now() + 24 * 60 * 60 * 1000)) {
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function toIsoFromLocal(value: string) {
  return new Date(value).toISOString();
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function typeLabel(value: string) {
  return TYPE_OPTIONS.find((option) => option.value === value)?.label ?? value;
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
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [dueAt, setDueAt] = useState(toLocalInputValue());
  const [type, setType] = useState<ApplicationReminderType>("follow_up");
  const [priority, setPriority] = useState<ApplicationReminderPriority>("normal");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runMutation(mutation: () => Promise<unknown>, busyValue: string | null) {
    setError(null);
    setBusyId(busyValue);
    try {
      await mutation();
      await onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update reminders");
    } finally {
      setBusyId(null);
      setCreating(false);
    }
  }

  async function submitCreate() {
    if (!title.trim() || !dueAt) {
      return;
    }
    setCreating(true);
    await runMutation(async () => {
      await createApplicationReminder(applicationId, {
        title: title.trim(),
        notes: notes.trim() || null,
        due_at: toIsoFromLocal(dueAt),
        reminder_type: type,
        priority,
        metadata: {},
      });
      setTitle("");
      setNotes("");
      setDueAt(toLocalInputValue());
      setType("follow_up");
      setPriority("normal");
    }, "create");
  }

  const now = Date.now();

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <div>
          <Text fw={600}>Reminders</Text>
          <Text size="sm" c="dimmed">
            Local follow-ups, deadlines, and next actions. These do not sync to
            calendars or send notifications.
          </Text>
        </div>

        <Stack gap="sm">
          <TextInput
            label="Reminder title"
            placeholder="Follow up with recruiter"
            value={title}
            onChange={(event) => setTitle(event.currentTarget.value)}
          />
          <Textarea
            label="Notes"
            placeholder="Optional reminder details"
            value={notes}
            onChange={(event) => setNotes(event.currentTarget.value)}
            autosize
            minRows={2}
          />
          <Group align="end">
            <TextInput
              label="Due date and time"
              type="datetime-local"
              value={dueAt}
              onChange={(event) => setDueAt(event.currentTarget.value)}
            />
            <Select
              label="Reminder type"
              value={type}
              data={TYPE_OPTIONS}
              onChange={(value) => setType((value as ApplicationReminderType) ?? "follow_up")}
            />
            <Select
              label="Priority"
              value={priority}
              data={PRIORITY_OPTIONS}
              onChange={(value) => setPriority((value as ApplicationReminderPriority) ?? "normal")}
            />
            <Button
              onClick={submitCreate}
              loading={creating}
              disabled={!title.trim() || !dueAt}
            >
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
          <Text c="dimmed" size="sm">
            No reminders yet.
          </Text>
        ) : (
          <Stack gap="sm">
            {reminders.map((reminder) => {
              const completed = reminder.completed_at !== null;
              const overdue = !completed && new Date(reminder.due_at).getTime() < now;
              return (
                <Card key={reminder.id} withBorder radius="sm" p="md">
                  <Group justify="space-between" align="flex-start">
                    <Stack gap={4}>
                      <Group gap="xs">
                        <Text fw={600}>{reminder.title}</Text>
                        <Badge color={overdue ? "red" : completed ? "gray" : "blue"}>
                          {completed ? "Completed" : overdue ? "Overdue" : "Open"}
                        </Badge>
                        <Badge variant="light">{typeLabel(reminder.reminder_type)}</Badge>
                        <Badge variant="outline">{reminder.priority}</Badge>
                      </Group>
                      <Text size="sm" c={overdue ? "red" : "dimmed"}>
                        Due {formatDateTime(reminder.due_at)}
                      </Text>
                      {reminder.notes ? <Text size="sm">{reminder.notes}</Text> : null}
                    </Stack>
                    <Group gap="xs">
                      {completed ? (
                        <Button
                          size="xs"
                          variant="outline"
                          loading={busyId === reminder.id}
                          onClick={() =>
                            runMutation(
                              () => reopenApplicationReminder(applicationId, reminder.id),
                              reminder.id,
                            )
                          }
                        >
                          Reopen
                        </Button>
                      ) : (
                        <Button
                          size="xs"
                          loading={busyId === reminder.id}
                          onClick={() =>
                            runMutation(
                              () => completeApplicationReminder(applicationId, reminder.id),
                              reminder.id,
                            )
                          }
                        >
                          Complete
                        </Button>
                      )}
                      <Button
                        size="xs"
                        color="red"
                        variant="subtle"
                        loading={busyId === `delete-${reminder.id}`}
                        onClick={() =>
                          runMutation(
                            () => deleteApplicationReminder(applicationId, reminder.id),
                            `delete-${reminder.id}`,
                          )
                        }
                      >
                        Archive
                      </Button>
                    </Group>
                  </Group>
                </Card>
              );
            })}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
