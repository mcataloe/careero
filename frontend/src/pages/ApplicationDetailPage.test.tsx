import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationDetailPage } from "./ApplicationDetailPage";
import { render, screen } from "../test-utils";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationInterviewStage,
  ApplicationNote,
  ApplicationReminder,
  ApplicationTimelineEvent,
} from "../types/applications";
import type { AdvisorPacket } from "../types/advisorPackets";
import type { AutomationSuggestionListResponse } from "../types/automation";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const application: ApplicationDetail = {
  id: "app-1",
  role_id: "role-1",
  workspace_id: "workspace-1",
  title: "Staff Platform Engineer",
  company: {
    id: "company-1",
    name: "Example Company",
    website_url: null,
  },
  current_state: "interested",
  applied_at: null,
  next_action_at: null,
  updated_at: "2026-05-16T15:00:00Z",
  archived_at: null,
  available_next_states: ["applied", "withdrawn", "archived"],
  counts: {
    notes: 1,
    external_links: 1,
    reminders: 0,
    interviews: 2,
  },
  workflow_metadata: {},
  application_state: {},
  state_history: [],
  role: {
    id: "role-1",
    workspace_id: "workspace-1",
    title: "Staff Platform Engineer",
    status: "interested",
    company: {
      id: "company-1",
      name: "Example Company",
      website_url: null,
    },
    job_url: "https://example.com/jobs/1",
    location: "Remote",
    remote_type: "remote",
  },
};

const timeline: ApplicationTimelineEvent[] = [
  {
    id: "created-1",
    application_id: "app-1",
    event_type: "application.created",
    title: "Application tracked",
    description: "Started tracking Staff Platform Engineer.",
    occurred_at: "2026-05-16T15:00:00Z",
    actor: "system",
    source_type: "application",
    source_id: "app-1",
    metadata: {},
  },
];

const notes: ApplicationNote[] = [
  {
    id: "note-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    author: "Local User",
    note_type: "recruiter",
    body: "Ask about team scope.",
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

const interviews: ApplicationInterviewStage[] = [
  {
    id: "interview-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    stage_type: "recruiter_screen",
    title: "Recruiter screen",
    scheduled_at: "2026-05-20T15:00:00Z",
    completed_at: null,
    status: "scheduled",
    interviewer_names: ["Recruiter One"],
    location_or_meeting_link: "https://meet.example.com/one",
    notes: null,
    preparation_notes: null,
    outcome_notes: null,
    metadata: {},
    state_transition_suggestion: "interviewing",
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

const links: ApplicationExternalLink[] = [
  {
    id: "link-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    label: "Job posting",
    url: "https://example.com/jobs/1",
    type: "job_posting",
    metadata: {},
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

const reminders: ApplicationReminder[] = [
  {
    id: "reminder-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    title: "Follow up with recruiter",
    notes: "Mention compensation range privately.",
    due_at: "2026-05-21T15:00:00Z",
    completed_at: null,
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

const automationSuggestions: AutomationSuggestionListResponse = {
  workspace_id: "workspace-1",
  target_type: "application",
  target_id: "app-1",
  external_actions_enabled: false,
  suggestions: [
    {
      id: "suggestion-1",
      workspace_id: "workspace-1",
      target_type: "application",
      target_id: "app-1",
      role_id: "role-1",
      application_id: "app-1",
      artifact_id: null,
      action_type: "communication_draft",
      title: "Prepare follow-up draft",
      summary: "A local-only follow-up draft can be reviewed.",
      reason: "Careero can prepare review text without sending it.",
      basis: "Generated from stored application timing only.",
      confidence: "Draft Only",
      source_inputs: {},
      preview: {
        title: "Draft follow-up note",
        body: "Hi, I wanted to briefly follow up.",
        content_hash: "sha256:test",
        external_mutation: false,
      },
      preview_hash: "sha256:test",
      status: "active",
      expires_at: null,
      policy_version: "automation_policy_v1",
      metadata: {},
      created_at: "2026-05-16T15:00:00Z",
      updated_at: "2026-05-16T15:00:00Z",
    },
  ],
};

const advisorPacket: AdvisorPacket = {
  packet_version: "advisor_packet.local_preview.v1",
  mode: "local_preview",
  generated_at: "2026-05-16T15:00:00Z",
  local_only: true,
  external_sharing_enabled: false,
  advisory_notice:
    "Local-only owner preview. Nothing is externally shared, no advisor account exists, and private strategy is redacted by default.",
  include_options: {
    artifact_ids: [],
    external_link_ids: [],
    interview_stage_ids: [],
    reminder_ids: [],
    advisor_context: null,
  },
  sections: [
    {
      key: "opportunity_summary",
      title: "Opportunity summary",
      status: "included",
      item_count: 1,
      warnings: [],
    },
    {
      key: "artifact_summaries",
      title: "Artifact summaries",
      status: "summary_only",
      item_count: 1,
      warnings: [],
    },
  ],
  opportunity: {
    id: "role-1",
    workspace_id: "workspace-1",
    title: "Staff Platform Engineer",
    company_name: "Example Company",
    status: "interested",
    location: "Remote",
    remote_type: "remote",
  },
  application: {
    id: "app-1",
    current_state: "interested",
    applied_at: null,
    next_action_at: null,
    counts: {
      notes: 1,
      reminders: 0,
      interviews: 1,
      external_links: 1,
    },
  },
  artifacts: [
    {
      id: "artifact-1",
      artifact_type: "cover_letter",
      title: "Cover letter",
      lifecycle_status: "draft",
      revision_number: 1,
      content_included: false,
      content: null,
      updated_at: "2026-05-16T15:00:00Z",
      warnings: [
        {
          code: "artifact_not_approved",
          message:
            "Generated artifact lifecycle is not approved; keep draft and truthfulness warnings visible before any future sharing flow.",
        },
      ],
    },
  ],
  selected_external_links: [],
  selected_interviews: [],
  selected_reminders: [],
  advisor_context: null,
  redactions: [
    {
      data_class: "Private user notes",
      field: "application_notes.body",
      default_visibility: "Private by default",
      status: "excluded",
      included: false,
      reason: "1 note(s) exist and require explicit future selection before inclusion.",
      warning: "Private notes are not advisor comments and remain separate.",
    },
    {
      data_class: "COMPASS score and explanation",
      field: "compass_evaluation",
      default_visibility: "Private by default",
      status: "excluded",
      included: false,
      reason: "Internal fit analysis remains advisory, source-grounded, and private by default.",
      warning: "COMPASS is advisory, not deterministic truth.",
    },
  ],
  warnings: [
    {
      code: "local_only_preview",
      message:
        "This packet is a local preview/export only. It does not create hosted access, invitations, accounts, public links, comments, or external sharing.",
    },
  ],
};

function renderDetailPage() {
  render(
    <MemoryRouter initialEntries={["/applications/app-1"]}>
      <Routes>
        <Route path="/applications/:applicationId" element={<ApplicationDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ApplicationDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders application summary and timeline", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(jsonResponse(timeline))
        .mockResolvedValueOnce(jsonResponse(notes))
        .mockResolvedValueOnce(jsonResponse(links))
        .mockResolvedValueOnce(jsonResponse(reminders))
        .mockResolvedValueOnce(jsonResponse(interviews))
        .mockResolvedValueOnce(jsonResponse(automationSuggestions))
        .mockResolvedValueOnce(jsonResponse(advisorPacket)),
    );

    renderDetailPage();

    expect(screen.getByText("Loading application")).toBeInTheDocument();
    expect(await screen.findByText("Staff Platform Engineer")).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("Application tracked")).toBeInTheDocument();
    expect(screen.getByText("Ask about team scope.")).toBeInTheDocument();
    expect(screen.getAllByText("Recruiter screen").length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: "Job posting" })[1]).toHaveAttribute(
      "rel",
      "noreferrer noopener",
    );
    expect(screen.getByText(/Notes: 1 - Links: 1 - Reminders: 0 - Interviews: 2/i)).toBeInTheDocument();
    expect(screen.getByText("Follow up with recruiter")).toBeInTheDocument();
    expect(screen.getByText("Prepare follow-up draft")).toBeInTheDocument();
    expect(screen.getByText(/Draft only. Careero will not send this message./i)).toBeInTheDocument();
    expect(screen.getByText("Advisor Packet Preview")).toBeInTheDocument();
    expect(screen.getByText("Local only")).toBeInTheDocument();
    expect(screen.getByText(/Local preview only\. Nothing is shared externally\./i)).toBeInTheDocument();
    expect(screen.getByText(/Reminder text can expose private deadlines or pressure points\. Review before including\./i)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: /Include reminder: Follow up with recruiter/i })).toBeInTheDocument();
    expect(screen.getByText(/This packet is a local preview\/export only\./i)).toBeInTheDocument();
    expect(screen.getByText("Private user notes")).toBeInTheDocument();
    expect(screen.getByText(/content excluded/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /share|send|invite/i })).not.toBeInTheDocument();
  });

  it("renders an error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "Application not found" }, 404)),
    );

    renderDetailPage();

    expect(await screen.findByText("Application not found")).toBeInTheDocument();
  });
});
