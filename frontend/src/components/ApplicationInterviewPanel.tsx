import {
  Alert,
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
  cancelApplicationInterview,
  completeApplicationInterview,
  createApplicationInterview,
  deleteApplicationInterview,
} from "../api/applications";
import type {
  ApplicationInterviewStage,
  ApplicationInterviewStagePayload,
  ApplicationInterviewStageType,
  ApplicationWorkflowState,
} from "../types/applications";

const STAGE_OPTIONS: { value: ApplicationInterviewStageType; label: string }[] = [
  { value: "recruiter_screen", label: "Recruiter screen" },
  { value: "hiring_manager", label: "Hiring manager" },
  { value: "technical", label: "Technical" },
  { value: "system_design", label: "System design" },
  { value: "behavioral", label: "Behavioral" },
  { value: "panel", label: "Panel" },
  { value: "final", label: "Final" },
  { value: "offer_discussion", label: "Offer discussion" },
  { value: "other", label: "Other" },
];

const STATUS_COLORS: Record<string, string> = {
  planned: "gray",
  scheduled: "blue",
  completed: "green",
  canceled: "orange",
  no_show: "red",
};

function stageLabel(value: string) {
  return STAGE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Not scheduled";
}

function toIsoFromDateTimeLocal(value: string) {
  if (!value) {
    return null;
  }
  return new Date(value).toISOString();
}

export function ApplicationInterviewPanel({
  applicationId,
  currentState,
  interviews,
  onChanged,
}: {
  applicationId: string;
  currentState: ApplicationWorkflowState;
  interviews: ApplicationInterviewStage[];
  onChanged: () => Promise<void>;
}) {
  const [title, setTitle] = useState("");
  const [stageType, setStageType] =
    useState<ApplicationInterviewStageType>("recruiter_screen");
  const [scheduledAt, setScheduledAt] = useState("");
  const [interviewers, setInterviewers] = useState("");
  const [location, setLocation] = useState("");
  const [preparationNotes, setPreparationNotes] = useState("");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasInterviewingSuggestion =
    currentState !== "interviewing" &&
    interviews.some((interview) => interview.state_transition_suggestion === "interviewing");

  async function runMutation(mutation: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await mutation();
      await onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update interviews");
    } finally {
      setBusy(false);
    }
  }

  async function submitCreate() {
    if (!title.trim()) {
      return;
    }
    const payload: ApplicationInterviewStagePayload = {
      title: title.trim(),
      stage_type: stageType,
      scheduled_at: toIsoFromDateTimeLocal(scheduledAt),
      interviewer_names: interviewers
        .split(",")
        .map((name) => name.trim())
        .filter(Boolean),
      location_or_meeting_link: location.trim() || null,
      preparation_notes: preparationNotes.trim() || null,
      notes: notes.trim() || null,
    };
    await runMutation(async () => {
      await createApplicationInterview(applicationId, payload);
      setTitle("");
      setScheduledAt("");
      setInterviewers("");
      setLocation("");
      setPreparationNotes("");
      setNotes("");
    });
  }

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <div>
          <Text fw={600}>Interviews</Text>
          <Text size="sm" c="dimmed">
            Manually track structured interview stages. Calendar invites, meeting
            generation, email, and coaching are intentionally out of scope.
          </Text>
        </div>

        {hasInterviewingSuggestion ? (
          <Alert color="blue" title="State transition available">
            You have interview activity. Move the application to interviewing from the
            workflow controls when you want to change state.
          </Alert>
        ) : null}

        <Stack gap="sm">
          <Group grow align="end">
            <TextInput
              label="Interview title"
              placeholder="Recruiter screen"
              value={title}
              onChange={(event) => setTitle(event.currentTarget.value)}
            />
            <Select
              label="Stage type"
              value={stageType}
              data={STAGE_OPTIONS}
              onChange={(value) =>
                setStageType((value as ApplicationInterviewStageType | null) ?? "other")
              }
            />
          </Group>
          <Group grow align="end">
            <TextInput
              label="Scheduled date and time"
              type="datetime-local"
              value={scheduledAt}
              onChange={(event) => setScheduledAt(event.currentTarget.value)}
            />
            <TextInput
              label="Interviewers"
              placeholder="Name one, Name two"
              value={interviewers}
              onChange={(event) => setInterviewers(event.currentTarget.value)}
            />
          </Group>
          <TextInput
            label="Location or meeting link"
            placeholder="Office address or meeting URL"
            value={location}
            onChange={(event) => setLocation(event.currentTarget.value)}
          />
          <Textarea
            label="Preparation notes"
            value={preparationNotes}
            onChange={(event) => setPreparationNotes(event.currentTarget.value)}
            autosize
            minRows={2}
          />
          <Textarea
            label="Notes"
            value={notes}
            onChange={(event) => setNotes(event.currentTarget.value)}
            autosize
            minRows={2}
          />
          <Group justify="flex-end">
            <Button onClick={submitCreate} loading={busy} disabled={!title.trim()}>
              Add interview
            </Button>
          </Group>
        </Stack>

        {error ? (
          <Text c="red" size="sm" role="alert">
            {error}
          </Text>
        ) : null}

        {interviews.length === 0 ? (
          <Text c="dimmed" size="sm">
            No interviews tracked yet.
          </Text>
        ) : (
          <Stack gap="sm">
            {interviews.map((interview) => (
              <Card key={interview.id} withBorder radius="sm" p="md">
                <Group justify="space-between" align="flex-start">
                  <Stack gap={4}>
                    <Group gap="xs">
                      <Text fw={600}>{interview.title}</Text>
                      <Badge color={STATUS_COLORS[interview.status] ?? "gray"}>
                        {interview.status}
                      </Badge>
                    </Group>
                    <Text size="sm" c="dimmed">
                      {stageLabel(interview.stage_type)} · {formatDate(interview.scheduled_at)}
                    </Text>
                    {interview.interviewer_names.length ? (
                      <Text size="sm">
                        Interviewers: {interview.interviewer_names.join(", ")}
                      </Text>
                    ) : null}
                    {interview.location_or_meeting_link ? (
                      <Text size="sm">{interview.location_or_meeting_link}</Text>
                    ) : null}
                    {interview.preparation_notes ? (
                      <Text size="sm">Prep: {interview.preparation_notes}</Text>
                    ) : null}
                    {interview.outcome_notes ? (
                      <Text size="sm">Outcome: {interview.outcome_notes}</Text>
                    ) : null}
                  </Stack>
                  <Group gap="xs">
                    <Button
                      size="xs"
                      variant="default"
                      onClick={() =>
                        runMutation(() =>
                          completeApplicationInterview(applicationId, interview.id),
                        )
                      }
                      loading={busy}
                    >
                      Complete
                    </Button>
                    <Button
                      size="xs"
                      variant="default"
                      color="orange"
                      onClick={() =>
                        runMutation(() =>
                          cancelApplicationInterview(applicationId, interview.id),
                        )
                      }
                      loading={busy}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="xs"
                      variant="outline"
                      color="red"
                      onClick={() =>
                        runMutation(() => deleteApplicationInterview(applicationId, interview.id))
                      }
                      loading={busy}
                    >
                      Delete
                    </Button>
                  </Group>
                </Group>
              </Card>
            ))}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
