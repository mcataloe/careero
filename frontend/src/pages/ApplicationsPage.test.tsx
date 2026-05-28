import { afterEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";

import { ApplicationsPage } from "./ApplicationsPage";
import { render, screen, waitFor } from "../test-utils";
import type { ApplicationPipelineResponse } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status >= 200 && status < 300 ? "OK" : "Error",
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const emptyPipeline: ApplicationPipelineResponse = {
  workspace_id: null,
  include_inactive: false,
  states: {
    discovered: [],
    interested: [],
    applied: [],
    interviewing: [],
    offer: [],
    rejected: [],
    withdrawn: [],
  },
};

const populatedPipeline: ApplicationPipelineResponse = {
  workspace_id: null,
  include_inactive: false,
  states: {
    discovered: [
      {
        id: "app-1",
        role_id: "role-1",
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
        current_state: "discovered",
        applied_at: null,
        next_action_at: null,
        updated_at: "2026-05-16T12:00:00Z",
        archived_at: null,
        available_next_states: ["interested", "withdrawn", "archived"],
        compass: null,
        resume_artifact: null,
        cover_letter_artifact: null,
        counts: {
          notes: 1,
          external_links: 3,
          reminders: 2,
          interviews: 0,
        },
      },
    ],
    interested: [],
    applied: [],
    interviewing: [],
    offer: [],
    rejected: [],
    withdrawn: [],
  },
};

describe("ApplicationsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders loading and empty states", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(emptyPipeline)));

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Loading applications")).toBeInTheDocument();
    expect(await screen.findByText("No application workflows yet.")).toBeInTheDocument();
  });

  it("renders an error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "Backend unavailable" }, 500)),
    );

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });

  it("groups applications by backend pipeline state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(populatedPipeline)));

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    expect((await screen.findAllByText("Staff Platform Engineer")).length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "Staff Platform Engineer" })).toHaveAttribute(
      "href",
      "/applications/app-1",
    );
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("Platform search")).toBeInTheDocument();
    expect(screen.getByText("Workflow attention")).toBeInTheDocument();
    expect(screen.getByText("1 notes")).toBeInTheDocument();
    expect(screen.getByText("3 links")).toBeInTheDocument();
    expect(screen.getByText("2 reminders")).toBeInTheDocument();
    expect(screen.getByText("Move to interested")).toBeInTheDocument();
    expect(screen.getByText("Move to withdrawn")).toBeInTheDocument();
    expect(screen.getByText("Move to archived")).toBeInTheDocument();
  });

  it("transitions through the API and refreshes the pipeline", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(populatedPipeline))
      .mockResolvedValueOnce(
        jsonResponse({
          ...populatedPipeline.states.discovered[0],
          current_state: "interested",
        }),
      )
      .mockResolvedValueOnce(jsonResponse(emptyPipeline));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    await userEvent.click(await screen.findByText("Move to interested"));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/applications/app-1/state-transitions",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ state: "interested", reactivate: false }),
        }),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/applications/pipeline", expect.any(Object));
  });

  it("shows transition errors without dropping pipeline cards", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(populatedPipeline))
      .mockResolvedValueOnce(jsonResponse({ detail: "Transition rejected" }, 409));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    await userEvent.click(await screen.findByText("Move to interested"));

    expect(await screen.findByText("Transition rejected")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Staff Platform Engineer" })).toBeInTheDocument();
  });

  it("requests archived workflows only when include archived is enabled", async () => {
    const archivedApplication = {
      ...populatedPipeline.states.discovered[0],
      id: "app-archived",
      current_state: "archived" as const,
      archived_at: "2026-05-17T15:00:00Z",
      available_next_states: ["discovered", "interested"],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(emptyPipeline))
      .mockResolvedValueOnce(
        jsonResponse({
          ...emptyPipeline,
          include_inactive: true,
          states: {
            ...emptyPipeline.states,
            archived: [archivedApplication],
          },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <ApplicationsPage />
      </MemoryRouter>,
    );

    await userEvent.click(await screen.findByLabelText("Include archived"));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/applications/pipeline?include_inactive=true",
        expect.any(Object),
      ),
    );
    expect(await screen.findByText("1 archived included")).toBeInTheDocument();
  });
});
