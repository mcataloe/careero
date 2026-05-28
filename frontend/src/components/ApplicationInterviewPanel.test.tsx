import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationInterviewPanel } from "./ApplicationInterviewPanel";
import { render, screen, userEvent } from "../test-utils";
import type { ApplicationInterviewStage } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const interview: ApplicationInterviewStage = {
  id: "interview-1",
  application_id: "app-1",
  workspace_id: "workspace-1",
  stage_type: "technical",
  title: "Technical interview",
  scheduled_at: "2026-05-20T15:00:00Z",
  completed_at: null,
  status: "scheduled",
  interviewer_names: ["Ada Lovelace"],
  location_or_meeting_link: "https://meet.example.com/abc",
  notes: null,
  preparation_notes: "Review system design notes.",
  outcome_notes: null,
  metadata: {},
  state_transition_suggestion: "interviewing",
  created_at: "2026-05-16T15:00:00Z",
  updated_at: "2026-05-16T15:00:00Z",
};

describe("ApplicationInterviewPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders empty state and creates an interview", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(interview, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationInterviewPanel
        applicationId="app-1"
        currentState="applied"
        interviews={[]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText(/No interviews tracked yet/)).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Interview title"), "Recruiter call");
    await userEvent.click(screen.getByRole("button", { name: "Add interview" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/interviews",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining('"title":"Recruiter call"'),
      }),
    );
    expect(onChanged).toHaveBeenCalled();
  });

  it("renders scheduled dates and completes or cancels interviews", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ ...interview, status: "completed" }))
      .mockResolvedValueOnce(jsonResponse({ ...interview, status: "canceled" }));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationInterviewPanel
        applicationId="app-1"
        currentState="applied"
        interviews={[interview]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText("Technical interview")).toBeInTheDocument();
    expect(screen.getByText(/Technical -/)).toBeInTheDocument();
    expect(screen.getByText("Upcoming or planned")).toBeInTheDocument();
    expect(screen.getByText(/Ada Lovelace/)).toBeInTheDocument();
    expect(screen.getByText("State transition available")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Complete" }));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/interviews/interview-1/complete",
      expect.objectContaining({ method: "POST" }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/applications/app-1/interviews/interview-1/cancel",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
