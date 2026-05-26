import { Badge, Card, Group, Stack, Text, Title } from "@mantine/core";
import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { getAdvisorPacket } from "../api/advisorPackets";
import { listAutomationSuggestions } from "../api/automation";
import {
  getApplication,
  getApplicationTimeline,
  listApplicationInterviews,
  listApplicationLinks,
  listApplicationNotes,
} from "../api/applications";
import { ApplicationInterviewPanel } from "../components/ApplicationInterviewPanel";
import { ApplicationLinksPanel } from "../components/ApplicationLinksPanel";
import { ApplicationNotesPanel } from "../components/ApplicationNotesPanel";
import { ApplicationTimeline } from "../components/ApplicationTimeline";
import { AdvisorPacketPanel } from "../components/AdvisorPacketPanel";
import { AutomationSuggestionsPanel } from "../components/AutomationSuggestionsPanel";
import { ErrorState, LoadingState } from "../components/States";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationInterviewStage,
  ApplicationNote,
  ApplicationTimelineEvent,
  ApplicationWorkflowState,
} from "../types/applications";
import type { AdvisorPacket } from "../types/advisorPackets";
import type { AutomationSuggestion } from "../types/automation";

const STATE_COLORS: Record<ApplicationWorkflowState, string> = {
  discovered: "gray",
  interested: "blue",
  applied: "teal",
  interviewing: "violet",
  offer: "green",
  rejected: "red",
  withdrawn: "orange",
  archived: "dark",
};

export function ApplicationDetailPage() {
  const { applicationId } = useParams();
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [timeline, setTimeline] = useState<ApplicationTimelineEvent[]>([]);
  const [notes, setNotes] = useState<ApplicationNote[]>([]);
  const [links, setLinks] = useState<ApplicationExternalLink[]>([]);
  const [interviews, setInterviews] = useState<ApplicationInterviewStage[]>([]);
  const [suggestions, setSuggestions] = useState<AutomationSuggestion[]>([]);
  const [advisorPacket, setAdvisorPacket] = useState<AdvisorPacket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadApplication() {
    if (!applicationId) {
      setError("Application id is required");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [
        nextApplication,
        nextTimeline,
        nextNotes,
        nextLinks,
        nextInterviews,
        nextSuggestions,
        nextAdvisorPacket,
      ] =
        await Promise.all([
          getApplication(applicationId),
          getApplicationTimeline(applicationId),
          listApplicationNotes(applicationId),
          listApplicationLinks(applicationId),
          listApplicationInterviews(applicationId),
          listAutomationSuggestions({
            targetType: "application",
            targetId: applicationId,
          }),
          getAdvisorPacket(applicationId),
        ]);
      setApplication(nextApplication);
      setTimeline(nextTimeline);
      setNotes(nextNotes);
      setLinks(nextLinks);
      setInterviews(nextInterviews);
      setSuggestions(nextSuggestions.suggestions);
      setAdvisorPacket(nextAdvisorPacket);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load application");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadApplication();
  }, [applicationId]);

  if (loading) {
    return <LoadingState label="Loading application" />;
  }

  if (error || !application) {
    return (
      <ErrorState
        message={error ?? "Application was not found"}
        onRetry={loadApplication}
      />
    );
  }

  return (
    <Stack gap="lg">
      <div>
        <Text component={Link} to="/applications" size="sm">
          Back to applications
        </Text>
        <Group justify="space-between" align="flex-start" mt="xs">
          <div>
            <Title order={1}>{application.title}</Title>
            <Text c="dimmed">{application.company.name}</Text>
          </div>
          <Badge color={STATE_COLORS[application.current_state]} variant="filled">
            {application.current_state}
          </Badge>
        </Group>
      </div>

      <Card withBorder radius="md" p="lg">
        <Stack gap="xs">
          <Text fw={600}>Workflow summary</Text>
          <Text size="sm" c="dimmed">
            Notes: {application.counts.notes} - Reminders:{" "}
            {application.counts.reminders} - Interviews:{" "}
            {application.counts.interviews}
          </Text>
          {application.role.job_url ? (
            <Text component="a" href={application.role.job_url} size="sm">
              Job posting
            </Text>
          ) : null}
        </Stack>
      </Card>

      <ApplicationInterviewPanel
        applicationId={application.id}
        currentState={application.current_state}
        interviews={interviews}
        onChanged={loadApplication}
      />

      <AutomationSuggestionsPanel
        suggestions={suggestions}
        title="Application suggestions"
        onChanged={loadApplication}
      />

      {advisorPacket ? (
        <AdvisorPacketPanel
          applicationId={application.id}
          packet={advisorPacket}
        />
      ) : null}

      <ApplicationNotesPanel
        applicationId={application.id}
        notes={notes}
        onChanged={loadApplication}
      />

      <ApplicationLinksPanel
        applicationId={application.id}
        links={links}
        onChanged={loadApplication}
      />

      <Stack gap="sm">
        <Title order={2}>Timeline</Title>
        <ApplicationTimeline events={timeline} />
      </Stack>
    </Stack>
  );
}
