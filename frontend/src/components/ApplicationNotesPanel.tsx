import {
  Button,
  Card,
  Group,
  Select,
  Stack,
  Text,
  Textarea,
} from "@mantine/core";
import { useState } from "react";

import {
  createApplicationNote,
  deleteApplicationNote,
  updateApplicationNote,
} from "../api/applications";
import type {
  ApplicationNote,
  ApplicationNotePayload,
  ApplicationNoteType,
} from "../types/applications";

const NOTE_TYPE_OPTIONS: { value: ApplicationNoteType; label: string }[] = [
  { value: "general", label: "General" },
  { value: "recruiter", label: "Recruiter" },
  { value: "compensation", label: "Compensation" },
  { value: "follow_up", label: "Follow-up" },
  { value: "interview", label: "Interview" },
];

function noteTypeLabel(value: string) {
  return NOTE_TYPE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function ApplicationNotesPanel({
  applicationId,
  notes,
  onChanged,
}: {
  applicationId: string;
  notes: ApplicationNote[];
  onChanged: () => Promise<void>;
}) {
  const [draftBody, setDraftBody] = useState("");
  const [draftType, setDraftType] = useState<ApplicationNoteType>("general");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editBody, setEditBody] = useState("");
  const [editType, setEditType] = useState<ApplicationNoteType>("general");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitCreate() {
    if (!draftBody.trim()) {
      return;
    }
    await runMutation(async () => {
      await createApplicationNote(applicationId, {
        body: draftBody.trim(),
        note_type: draftType,
      });
      setDraftBody("");
      setDraftType("general");
    });
  }

  function startEdit(note: ApplicationNote) {
    setEditingId(note.id);
    setEditBody(note.body);
    setEditType(note.note_type);
    setError(null);
  }

  async function submitEdit(noteId: string) {
    if (!editBody.trim()) {
      return;
    }
    const payload: ApplicationNotePayload = {
      body: editBody.trim(),
      note_type: editType,
    };
    await runMutation(async () => {
      await updateApplicationNote(applicationId, noteId, payload);
      setEditingId(null);
    });
  }

  async function deleteNote(noteId: string) {
    await runMutation(async () => {
      await deleteApplicationNote(applicationId, noteId);
      if (editingId === noteId) {
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
      setError(err instanceof Error ? err.message : "Could not update notes");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <div>
          <Text fw={600}>Notes</Text>
          <Text size="sm" c="dimmed">
            Track application-specific context without mixing it into reminders or
            interviews.
          </Text>
        </div>

        <Stack gap="sm">
          <Textarea
            label="New note"
            placeholder="Add a note for this application"
            value={draftBody}
            onChange={(event) => setDraftBody(event.currentTarget.value)}
            autosize
            minRows={3}
            maxRows={8}
          />
          <Group justify="space-between" align="end">
            <Select
              label="Note type"
              value={draftType}
              data={NOTE_TYPE_OPTIONS}
              onChange={(value) =>
                setDraftType((value as ApplicationNoteType | null) ?? "general")
              }
              w={{ base: "100%", sm: 220 }}
            />
            <Button onClick={submitCreate} loading={busy} disabled={!draftBody.trim()}>
              Add note
            </Button>
          </Group>
        </Stack>

        {error ? (
          <Text c="red" size="sm" role="alert">
            {error}
          </Text>
        ) : null}

        {notes.length === 0 ? (
          <Card withBorder radius="sm" p="md">
            <Text c="dimmed" size="sm">
              No notes yet. Add recruiter context, compensation details, or follow-up
              rationale when there is something worth preserving.
            </Text>
          </Card>
        ) : (
          <Stack gap="sm">
            {notes.map((note) => (
              <Card key={note.id} withBorder radius="sm" p="md">
                {editingId === note.id ? (
                  <Stack gap="sm">
                    <Textarea
                      label="Edit note"
                      value={editBody}
                      onChange={(event) => setEditBody(event.currentTarget.value)}
                      autosize
                      minRows={3}
                      maxRows={8}
                    />
                    <Group justify="space-between" align="end">
                      <Select
                        label="Note type"
                        value={editType}
                        data={NOTE_TYPE_OPTIONS}
                        onChange={(value) =>
                          setEditType(
                            (value as ApplicationNoteType | null) ?? "general",
                          )
                        }
                        w={{ base: "100%", sm: 220 }}
                      />
                      <Group gap="xs">
                        <Button
                          variant="default"
                          onClick={() => setEditingId(null)}
                          disabled={busy}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={() => submitEdit(note.id)}
                          loading={busy}
                          disabled={!editBody.trim()}
                        >
                          Save note
                        </Button>
                      </Group>
                    </Group>
                  </Stack>
                ) : (
                  <Stack gap="xs">
                    <Group justify="space-between" align="flex-start">
                      <div>
                        <Text size="xs" c="dimmed">
                          {noteTypeLabel(note.note_type)}
                        </Text>
                        <Text size="xs" c="dimmed">
                          Created {formatDateTime(note.created_at)}
                          {note.updated_at !== note.created_at
                            ? ` - Updated ${formatDateTime(note.updated_at)}`
                            : ""}
                        </Text>
                        <Text style={{ whiteSpace: "pre-wrap" }}>{note.body}</Text>
                      </div>
                      <Group gap="xs">
                        <Button
                          size="xs"
                          variant="default"
                          onClick={() => startEdit(note)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="xs"
                          variant="outline"
                          color="red"
                          onClick={() => deleteNote(note.id)}
                          loading={busy}
                        >
                          Delete
                        </Button>
                      </Group>
                    </Group>
                  </Stack>
                )}
              </Card>
            ))}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
