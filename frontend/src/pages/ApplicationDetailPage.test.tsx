import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationDetailPage } from "./ApplicationDetailPage";
import { render, screen } from "../test-utils";
import type {
  ApplicationDetail,
  ApplicationExternalLink,
  ApplicationNote,
  ApplicationTimelineEvent,
} from "../types/applications";

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
        .mockResolvedValueOnce(jsonResponse(links)),
    );

    renderDetailPage();

    expect(screen.getByText("Loading application")).toBeInTheDocument();
    expect(await screen.findByText("Staff Platform Engineer")).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("Application tracked")).toBeInTheDocument();
    expect(screen.getByText("Ask about team scope.")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Job posting" })[1]).toHaveAttribute(
      "rel",
      "noreferrer noopener",
    );
    expect(screen.getByText(/Notes: 1 - Reminders: 0 - Interviews: 2/i)).toBeInTheDocument();
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
