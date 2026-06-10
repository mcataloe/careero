import { MemoryRouter, Route, Routes } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationDetailPage } from "./ApplicationDetailPage";
import { render, screen } from "../test-utils";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationInterviewStage,
  ApplicationReminder,
  ApplicationTimelineEvent,
} from "../types/applications";
import type { AdvisorPacket } from "../types/advisorPackets";
import type { ArtifactRecord } from "../types/artifacts";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

function blobResponse(
  response: Blob,
  headers: Record<string, string> = {},
  status = 200,
) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers(headers),
    blob: vi.fn().mockResolvedValue(response),
    json: vi.fn().mockRejectedValue(new Error("Export response is not JSON")),
  };
}

function stubDownloadUrl() {
  const createObjectURL = vi.fn().mockReturnValue("blob:careero-artifact");
  const revokeObjectURL = vi.fn();
  const anchorClick = vi
    .spyOn(HTMLAnchorElement.prototype, "click")
    .mockImplementation(() => undefined);
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    value: createObjectURL,
  });
  Object.defineProperty(URL, "revokeObjectURL", {
    configurable: true,
    value: revokeObjectURL,
  });
  return { anchorClick, createObjectURL, revokeObjectURL };
}

const originalCreateObjectURL = URL.createObjectURL;
const originalRevokeObjectURL = URL.revokeObjectURL;

const application: ApplicationDetail = {
  id: "app-1",
  role_id: "role-1",
  opportunity_id: "role-1",
  workspace_id: "workspace-1",
  workspace: {
    id: "workspace-1",
    title: "Platform search",
    status: "active",
  },
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
  compass: null,
  resume_artifact: null,
  cover_letter_artifact: null,
  counts: {
    notes: 1,
    external_links: 1,
    reminders: 0,
    interviews: 2,
  },
  workflow_metadata: {},
  application_state: {},
  state_history: [],
  opportunity: {
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
          code: "artifact_not_submitted",
          message:
            "Generated artifact lifecycle is not submitted; keep draft, review, and truthfulness warnings visible before any future sharing flow.",
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

const resumeArtifact: ArtifactRecord = {
  id: "artifact-resume-1",
  workspace_id: "workspace-1",
  application_id: "app-1",
  role_id: "role-1",
  opportunity_id: "role-1",
  artifact_type: "tailored_resume",
  lifecycle_status: "draft",
  version_number: 1,
  title: "Targeted resume",
  content: "Employer-facing resume content.",
  reviewed_at: null,
  submitted_at: null,
  archived_at: null,
  created_at: "2026-05-16T15:00:00Z",
  updated_at: "2026-05-16T15:00:00Z",
  traceability: {
    workspace_id: "workspace-1",
    role_id: "role-1",
    opportunity_id: "role-1",
    application_id: "app-1",
    evaluation_id: "evaluation-1",
    source_resume_version_id: "source-version-1",
    source_artifact_id: null,
    parent_artifact_id: null,
    generation_warnings: [],
    export_formats: ["md"],
  },
  available_transitions: ["reviewed", "archived"],
  new_version_created: false,
  source_submitted_artifact_id: null,
  metadata: {
    revision_id: "revision-1",
    change_summary: "Initial draft.",
  },
};

const submittedCoverLetterArtifact: ArtifactRecord = {
  ...resumeArtifact,
  id: "artifact-cover-1",
  artifact_type: "cover_letter",
  lifecycle_status: "submitted",
  title: "Submitted cover letter",
  content: "Employer-facing cover letter content.",
  reviewed_at: "2026-05-17T15:00:00Z",
  submitted_at: "2026-05-18T15:00:00Z",
  available_transitions: ["archived"],
};

function renderDetailPage(path = "/applications/app-1/overview") {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/applications/:applicationId" element={<ApplicationDetailPage />} />
        <Route
          path="/applications/:applicationId/:section"
          element={<ApplicationDetailPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ApplicationDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    if (originalCreateObjectURL) {
      Object.defineProperty(URL, "createObjectURL", {
        configurable: true,
        value: originalCreateObjectURL,
      });
    } else {
      Reflect.deleteProperty(URL, "createObjectURL");
    }
    if (originalRevokeObjectURL) {
      Object.defineProperty(URL, "revokeObjectURL", {
        configurable: true,
        value: originalRevokeObjectURL,
      });
    } else {
      Reflect.deleteProperty(URL, "revokeObjectURL");
    }
  });

  it("renders application overview and local navigation", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse(application)),
    );

    renderDetailPage();

    expect(screen.getByText("Loading application")).toBeInTheDocument();
    expect(await screen.findByText("Staff Platform Engineer")).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("Platform search")).toBeInTheDocument();
    expect(screen.getByText("Current status")).toBeInTheDocument();
    expect(screen.getByText("Workflow overview")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /timeline/i })[0]).toHaveAttribute(
      "href",
      "/applications/app-1/timeline",
    );
    expect(screen.queryByText("Application tracked")).not.toBeInTheDocument();
  });

  it("renders advisor packet route without sharing actions", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(jsonResponse(advisorPacket))
        .mockResolvedValueOnce(jsonResponse(links))
        .mockResolvedValueOnce(jsonResponse(interviews))
        .mockResolvedValueOnce(jsonResponse(reminders)),
    );

    renderDetailPage("/applications/app-1/advisor-packet");

    expect(await screen.findByText("Advisor Packet Preview")).toBeInTheDocument();
    expect(screen.getByText("Local only")).toBeInTheDocument();
    expect(screen.getByText(/Local preview only\. Nothing is shared externally\./i)).toBeInTheDocument();
    expect(screen.getByText(/Reminder text can expose private deadlines or pressure points\. Review before including\./i)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: /Include reminder: Follow up with recruiter/i })).toBeInTheDocument();
    expect(screen.getByText(/This packet is a local preview\/export only\./i)).toBeInTheDocument();
    expect(screen.getByText("Private user notes")).toBeInTheDocument();
    expect(screen.getByText("COMPASS score and explanation")).toBeInTheDocument();
    expect(screen.getByText(/Internal fit analysis remains advisory/i)).toBeInTheDocument();
    expect(screen.getByText(/content excluded/i)).toBeInTheDocument();
    expect(screen.queryByText(/Latest COMPASS rationale before tailoring/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /share|send|invite/i })).not.toBeInTheDocument();
  });

  it("renders timeline route independently", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(jsonResponse(timeline)),
    );

    renderDetailPage("/applications/app-1/timeline");

    expect(await screen.findByText("Application tracked")).toBeInTheDocument();
    expect(screen.queryByText("Ask about team scope.")).not.toBeInTheDocument();
  });

  it("renders timeline empty and error states", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(jsonResponse([])),
    );

    renderDetailPage("/applications/app-1/timeline");

    expect(
      await screen.findByText("No timeline events recorded yet."),
    ).toBeInTheDocument();

    vi.unstubAllGlobals();
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(
          jsonResponse({ detail: "Timeline unavailable" }, 500),
        ),
    );

    renderDetailPage("/applications/app-1/timeline");

    expect(await screen.findByText("Timeline unavailable")).toBeInTheDocument();
  });

  it("renders artifact lifecycle status and employer-facing detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(
          jsonResponse([resumeArtifact, submittedCoverLetterArtifact]),
        ),
    );

    renderDetailPage("/applications/app-1/artifacts");

    expect(
      await screen.findByRole("heading", { name: "Artifacts" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Resume artifacts")).toBeInTheDocument();
    expect(screen.getByText("Cover-letter artifacts")).toBeInTheDocument();
    expect(screen.getAllByText("Targeted resume").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Submitted cover letter").length).toBeGreaterThan(0);
    expect(screen.getByText("Employer-facing resume content.")).toBeInTheDocument();
    expect(screen.getByText("Submitted versions")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /download markdown/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /download docx/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /download pdf/i })).toBeInTheDocument();
    expect(screen.queryByText(/ATS risk|private strategy/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: /share|send|invite|cloud|sync|upload|publish/i,
      }),
    ).not.toBeInTheDocument();
  });

  it("downloads selected artifact exports with the backend filename", async () => {
    const { anchorClick, createObjectURL, revokeObjectURL } = stubDownloadUrl();
    const refreshedArtifact = {
      ...resumeArtifact,
      traceability: {
        ...resumeArtifact.traceability,
        export_formats: ["md", "docx"],
      },
    };
    const exportResponse = blobResponse(
      new Blob(["docx bytes"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      }),
      {
        "content-disposition": 'attachment; filename="targeted-resume.docx"',
        "x-careero-content-hash": "sha256:test-hash",
      },
    );
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(jsonResponse([resumeArtifact]))
      .mockResolvedValueOnce(exportResponse)
      .mockResolvedValueOnce(jsonResponse([refreshedArtifact]))
      .mockResolvedValueOnce(jsonResponse(application));
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage("/applications/app-1/artifacts");

    await userEvent.click(await screen.findByRole("button", { name: /download docx/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/artifacts/artifact-resume-1/exports/docx",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
    expect(exportResponse.blob).toHaveBeenCalled();
    expect(exportResponse.json).not.toHaveBeenCalled();
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
    expect(anchorClick).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:careero-artifact");
    expect(await screen.findByText("Downloaded DOCX export locally.")).toBeInTheDocument();
    expect(await screen.findByText("DOCX")).toBeInTheDocument();
  });

  it("shows dismissible artifact export errors", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(jsonResponse([resumeArtifact]))
      .mockResolvedValueOnce(
        jsonResponse({ detail: "PDF export requires local dependencies" }, 503),
      );
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage("/applications/app-1/artifacts");

    await userEvent.click(await screen.findByRole("button", { name: /download pdf/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/artifacts/artifact-resume-1/exports/pdf",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
    expect(
      await screen.findByText("PDF export requires local dependencies"),
    ).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /dismiss export error/i }));
    expect(
      screen.queryByText("PDF export requires local dependencies"),
    ).not.toBeInTheDocument();
  });

  it("renders artifact empty state", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(jsonResponse([])),
    );

    renderDetailPage("/applications/app-1/artifacts");

    expect(await screen.findByText("No artifacts yet")).toBeInTheDocument();
    expect(
      screen.getByText(/Generate or create a resume draft or cover-letter draft/i),
    ).toBeInTheDocument();
  });

  it("marks artifact reviewed and refreshes application artifacts", async () => {
    const reviewedArtifact = {
      ...resumeArtifact,
      lifecycle_status: "reviewed",
      reviewed_at: "2026-05-17T15:00:00Z",
      available_transitions: ["submitted", "archived"],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(jsonResponse([resumeArtifact]))
      .mockResolvedValueOnce(jsonResponse(reviewedArtifact))
      .mockResolvedValueOnce(jsonResponse([reviewedArtifact]))
      .mockResolvedValueOnce(jsonResponse(application));
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage("/applications/app-1/artifacts");

    await userEvent.click(await screen.findByRole("button", { name: /review/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/artifacts/artifact-resume-1/review",
      expect.objectContaining({ method: "POST" }),
    );
    expect(await screen.findByText("Artifact marked reviewed.")).toBeInTheDocument();
  });

  it("creates a draft revision from a submitted artifact", async () => {
    const newDraft = {
      ...submittedCoverLetterArtifact,
      id: "artifact-cover-2",
      lifecycle_status: "draft",
      submitted_at: null,
      source_submitted_artifact_id: "artifact-cover-1",
      traceability: {
        ...submittedCoverLetterArtifact.traceability,
        source_artifact_id: "artifact-cover-1",
      },
      available_transitions: ["reviewed", "archived"],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(jsonResponse([submittedCoverLetterArtifact]))
      .mockResolvedValueOnce(jsonResponse(newDraft))
      .mockResolvedValueOnce(jsonResponse([newDraft]))
      .mockResolvedValueOnce(jsonResponse(application));
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage("/applications/app-1/artifacts");

    await userEvent.click(await screen.findByRole("button", { name: /new draft/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/artifacts/artifact-cover-1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          title: "Submitted cover letter",
          content: "Employer-facing cover letter content.",
          change_summary: "Created a new draft from submitted artifact.",
        }),
      }),
    );
    expect(await screen.findByText("New draft version created.")).toBeInTheDocument();
  });

  it("updates application status from visible controls", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(
        jsonResponse({
          ...application,
          current_state: "applied",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          ...application,
          current_state: "applied",
          available_next_states: ["interviewing", "rejected", "withdrawn", "archived"],
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage();

    await userEvent.click(await screen.findByRole("button", { name: /move to applied/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/state-transitions",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ state: "applied", reactivate: false }),
      }),
    );
    expect(await screen.findByText("Application moved to applied")).toBeInTheDocument();
  });

  it("shows dismissible feedback when status update fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(application))
        .mockResolvedValueOnce(
          jsonResponse({ detail: "Unsupported transition" }, 409),
        ),
    );

    renderDetailPage();

    await userEvent.click(await screen.findByRole("button", { name: /move to applied/i }));

    expect(await screen.findByText("Unsupported transition")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /dismiss error/i }));
    expect(screen.queryByText("Unsupported transition")).not.toBeInTheDocument();
  });

  it("requires confirmation before archive transitions", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(application))
      .mockResolvedValueOnce(
        jsonResponse({
          ...application,
          current_state: "archived",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          ...application,
          current_state: "archived",
          archived_at: "2026-05-17T15:00:00Z",
          available_next_states: ["discovered", "interested"],
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    renderDetailPage();

    await userEvent.click(await screen.findByRole("button", { name: "Archive" }));
    expect(screen.getByRole("button", { name: "Confirm archive" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Confirm archive" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/state-transitions",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ state: "archived", reactivate: false }),
      }),
    );
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
