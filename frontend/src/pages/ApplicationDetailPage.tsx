import { Badge, Card, Group, Stack, Text, Title } from "@mantine/core";
import { Link, Navigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { getAdvisorPacket } from "../api/advisorPackets";
import { listAutomationSuggestions } from "../api/automation";
import {
  getApplication,
  getApplicationTimeline,
  listApplicationInterviews,
  listApplicationLinks,
  listApplicationNotes,
  listApplicationReminders,
} from "../api/applications";
import { ApplicationInterviewPanel } from "../components/ApplicationInterviewPanel";
import { ApplicationLinksPanel } from "../components/ApplicationLinksPanel";
import { ApplicationNotesPanel } from "../components/ApplicationNotesPanel";
import { ApplicationRemindersPanel } from "../components/ApplicationRemindersPanel";
import { ApplicationTimeline } from "../components/ApplicationTimeline";
import { AdvisorPacketPanel } from "../components/AdvisorPacketPanel";
import { AutomationSuggestionsPanel } from "../components/AutomationSuggestionsPanel";
import { FeatureWorkspaceLayout } from "../components/FeatureWorkspaceLayout";
import { ErrorState, LoadingState } from "../components/States";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationInterviewStage,
  ApplicationNote,
  ApplicationReminder,
  ApplicationTimelineEvent,
  ApplicationWorkflowState,
} from "../types/applications";
import type {
  AdvisorPacket,
  AdvisorPacketPreviewOptions,
} from "../types/advisorPackets";
import type {
  AutomationSuggestionListResponse,
} from "../types/automation";

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

const applicationSections = [
  {
    id: "overview",
    label: "Overview",
    description: "Workflow counts and posting link",
  },
  {
    id: "interviews",
    label: "Interviews",
    description: "Structured interview tracking",
  },
  {
    id: "reminders",
    label: "Reminders",
    description: "Follow-up and next action dates",
  },
  {
    id: "suggestions",
    label: "Suggestions",
    description: "Local automation suggestions",
  },
  {
    id: "advisor-packet",
    label: "Advisor packet",
    description: "Local-only preview and export",
  },
  {
    id: "notes",
    label: "Notes",
    description: "Private application notes",
  },
  {
    id: "links",
    label: "Links",
    description: "External references",
  },
  {
    id: "timeline",
    label: "Timeline",
    description: "Workflow history",
  },
] as const;

type ApplicationSectionId = (typeof applicationSections)[number]["id"];

const applicationSectionIds = new Set<string>(
  applicationSections.map((section) => section.id),
);

export function ApplicationDetailPage() {
  const { applicationId, section } = useParams();
  const activeSection = isApplicationSectionId(section) ? section : null;
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
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
      setApplication(await getApplication(applicationId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load application");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadApplication();
  }, [applicationId]);

  if (!activeSection) {
    return <Navigate to={`/applications/${applicationId ?? ""}/overview`} replace />;
  }

  if (loading) {
    return <LoadingState label="Loading application" />;
  }

  if (error || !application || !applicationId) {
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

      <FeatureWorkspaceLayout
        navLabel="Application sections"
        items={applicationSections.map((item) => ({
          ...item,
          to: `/applications/${application.id}/${item.id}`,
        }))}
        activeId={activeSection}
        withDetailPanel={activeSection === "overview"}
      >
        <ApplicationSectionContent
          activeSection={activeSection}
          application={application}
          applicationId={applicationId}
          onApplicationChanged={loadApplication}
        />
      </FeatureWorkspaceLayout>
    </Stack>
  );
}

function ApplicationSectionContent({
  activeSection,
  application,
  applicationId,
  onApplicationChanged,
}: {
  activeSection: ApplicationSectionId;
  application: ApplicationDetail;
  applicationId: string;
  onApplicationChanged: () => void;
}) {
  switch (activeSection) {
    case "interviews":
      return (
        <ApplicationInterviewsSection
          applicationId={applicationId}
          currentState={application.current_state}
          onApplicationChanged={onApplicationChanged}
        />
      );
    case "reminders":
      return (
        <ApplicationRemindersSection
          applicationId={applicationId}
          onApplicationChanged={onApplicationChanged}
        />
      );
    case "suggestions":
      return <ApplicationSuggestionsSection applicationId={applicationId} />;
    case "advisor-packet":
      return <ApplicationAdvisorPacketSection applicationId={applicationId} />;
    case "notes":
      return <ApplicationNotesSection applicationId={applicationId} />;
    case "links":
      return <ApplicationLinksSection applicationId={applicationId} />;
    case "timeline":
      return <ApplicationTimelineSection applicationId={applicationId} />;
    case "overview":
    default:
      return <ApplicationOverviewSection application={application} />;
  }
}

function ApplicationOverviewSection({
  application,
}: {
  application: ApplicationDetail;
}) {
  return (
    <Stack gap="xs">
      <Text fw={600}>Workflow summary</Text>
      <Text size="sm" c="dimmed">
        Notes: {application.counts.notes} - Links:{" "}
        {application.counts.external_links} - Reminders:{" "}
        {application.counts.reminders} - Interviews:{" "}
        {application.counts.interviews}
      </Text>
      {application.role.job_url ? (
        <Text component="a" href={application.role.job_url} size="sm">
          Job posting
        </Text>
      ) : null}
    </Stack>
  );
}

function ApplicationInterviewsSection({
  applicationId,
  currentState,
  onApplicationChanged,
}: {
  applicationId: string;
  currentState: ApplicationWorkflowState;
  onApplicationChanged: () => void;
}) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading interviews"
      errorMessage="Could not load interviews"
      load={() => listApplicationInterviews(applicationId)}
    >
      {(interviews: ApplicationInterviewStage[], reload) => (
        <ApplicationInterviewPanel
          applicationId={applicationId}
          currentState={currentState}
          interviews={interviews}
          onChanged={async () => {
            await reload();
            onApplicationChanged();
          }}
        />
      )}
    </AsyncApplicationSection>
  );
}

function ApplicationRemindersSection({
  applicationId,
  onApplicationChanged,
}: {
  applicationId: string;
  onApplicationChanged: () => void;
}) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading reminders"
      errorMessage="Could not load reminders"
      load={() => listApplicationReminders(applicationId)}
    >
      {(reminders: ApplicationReminder[], reload) => (
        <ApplicationRemindersPanel
          applicationId={applicationId}
          reminders={reminders}
          onChanged={async () => {
            await reload();
            onApplicationChanged();
          }}
        />
      )}
    </AsyncApplicationSection>
  );
}

function ApplicationSuggestionsSection({
  applicationId,
}: {
  applicationId: string;
}) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading application suggestions"
      errorMessage="Could not load application suggestions"
      load={() =>
        listAutomationSuggestions({
          targetType: "application",
          targetId: applicationId,
        })
      }
    >
      {(response: AutomationSuggestionListResponse, reload) => (
        <AutomationSuggestionsPanel
          suggestions={response.suggestions}
          title="Application suggestions"
          onChanged={reload}
        />
      )}
    </AsyncApplicationSection>
  );
}

function ApplicationAdvisorPacketSection({
  applicationId,
}: {
  applicationId: string;
}) {
  const [packet, setPacket] = useState<AdvisorPacket | null>(null);
  const [links, setLinks] = useState<ApplicationExternalLink[]>([]);
  const [interviews, setInterviews] = useState<ApplicationInterviewStage[]>([]);
  const [reminders, setReminders] = useState<ApplicationReminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAdvisorPacket() {
    setLoading(true);
    setError(null);
    try {
      const [
        nextAdvisorPacket,
        nextLinks,
        nextInterviews,
        nextReminders,
      ] = await Promise.all([
        getAdvisorPacket(applicationId),
        listApplicationLinks(applicationId),
        listApplicationInterviews(applicationId),
        listApplicationReminders(applicationId),
      ]);
      setPacket(nextAdvisorPacket);
      setLinks(nextLinks);
      setInterviews(nextInterviews);
      setReminders(nextReminders);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load advisor packet");
    } finally {
      setLoading(false);
    }
  }

  async function refreshAdvisorPacket(options: AdvisorPacketPreviewOptions) {
    const nextAdvisorPacket = await getAdvisorPacket(applicationId, options);
    setPacket(nextAdvisorPacket);
  }

  useEffect(() => {
    void loadAdvisorPacket();
  }, [applicationId]);

  if (loading) {
    return <LoadingState label="Loading advisor packet" />;
  }

  if (error || !packet) {
    return (
      <ErrorState
        message={error ?? "Advisor packet was not available"}
        onRetry={loadAdvisorPacket}
      />
    );
  }

  return (
    <AdvisorPacketPanel
      applicationId={applicationId}
      packet={packet}
      externalLinks={links}
      interviews={interviews}
      reminders={reminders}
      onRefresh={refreshAdvisorPacket}
    />
  );
}

function ApplicationNotesSection({ applicationId }: { applicationId: string }) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading notes"
      errorMessage="Could not load notes"
      load={() => listApplicationNotes(applicationId)}
    >
      {(notes: ApplicationNote[], reload) => (
        <ApplicationNotesPanel
          applicationId={applicationId}
          notes={notes}
          onChanged={reload}
        />
      )}
    </AsyncApplicationSection>
  );
}

function ApplicationLinksSection({ applicationId }: { applicationId: string }) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading links"
      errorMessage="Could not load links"
      load={() => listApplicationLinks(applicationId)}
    >
      {(links: ApplicationExternalLink[], reload) => (
        <ApplicationLinksPanel
          applicationId={applicationId}
          links={links}
          onChanged={reload}
        />
      )}
    </AsyncApplicationSection>
  );
}

function ApplicationTimelineSection({ applicationId }: { applicationId: string }) {
  return (
    <AsyncApplicationSection
      loadingLabel="Loading timeline"
      errorMessage="Could not load timeline"
      load={() => getApplicationTimeline(applicationId)}
    >
      {(timeline: ApplicationTimelineEvent[]) => (
        <Card withBorder radius="md" p="lg">
          <Stack gap="sm">
            <Title order={2}>Timeline</Title>
            <ApplicationTimeline events={timeline} />
          </Stack>
        </Card>
      )}
    </AsyncApplicationSection>
  );
}

function AsyncApplicationSection<T>({
  loadingLabel,
  errorMessage,
  load,
  children,
}: {
  loadingLabel: string;
  errorMessage: string;
  load: () => Promise<T>;
  children: (data: T, reload: () => Promise<void>) => React.ReactNode;
}) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      setData(await load());
    } catch (err) {
      setError(err instanceof Error ? err.message : errorMessage);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  if (loading) {
    return <LoadingState label={loadingLabel} />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? errorMessage} onRetry={loadData} />;
  }

  return <>{children(data, loadData)}</>;
}

function isApplicationSectionId(
  value: string | undefined,
): value is ApplicationSectionId {
  return typeof value === "string" && applicationSectionIds.has(value);
}
