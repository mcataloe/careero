import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RoleDetailPage } from "./RoleDetailPage";
import { sampleEvaluation, sampleRole } from "../test-data";
import { render, screen, userEvent, waitFor } from "../test-utils";
import type { ApplicationDetail } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

function renderPage(path = `/opportunities/${sampleRole.id}/compass`) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route
          path="/opportunities/:opportunityId"
          element={<RoleDetailPage />}
        />
        <Route
          path="/opportunities/:opportunityId/:section"
          element={<RoleDetailPage />}
        />
        <Route path="/opportunities" element={<div>Opportunities</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

const sampleApplication: ApplicationDetail = {
  id: "app-1",
  role_id: sampleRole.id,
  opportunity_id: sampleRole.id,
  workspace_id: "workspace-1",
  workspace: {
    id: "workspace-1",
    title: "Platform search",
    status: "active",
  },
  title: sampleRole.title,
  company: sampleRole.company,
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
    external_links: 0,
    reminders: 2,
    interviews: 1,
  },
  workflow_metadata: {},
  application_state: {},
  state_history: [],
  opportunity: {
    id: sampleRole.id,
    workspace_id: "workspace-1",
    title: sampleRole.title,
    status: sampleRole.status,
    company: sampleRole.company,
    job_url: sampleRole.job_url,
    location: sampleRole.location,
    remote_type: sampleRole.remote_type,
  },
  role: {
    id: sampleRole.id,
    workspace_id: "workspace-1",
    title: sampleRole.title,
    status: sampleRole.status,
    company: sampleRole.company,
    job_url: sampleRole.job_url,
    location: sampleRole.location,
    remote_type: sampleRole.remote_type,
  },
};

describe("RoleDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("runs evaluation from a not-evaluated role and displays the result", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation, 201));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Not evaluated")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/opportunities/${sampleRole.id}`,
      expect.any(Object),
    );
    await user.click(screen.getByRole("button", { name: /run compass evaluation/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/roles/${sampleRole.id}/evaluations`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(JSON.parse(fetchMock.mock.calls[2][1].body as string)).toEqual({
      user_context: {},
    });
    expect(await screen.findByText("COMPASS evaluation completed")).toBeInTheDocument();
    expect(screen.getByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
  });

  it("renders section navigation with valid role detail targets", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404));
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    expect(await screen.findByRole("link", { name: /overview/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/overview`,
    );
    expect(screen.getByRole("link", { name: /^description/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/description`,
    );
    expect(screen.getByRole("link", { name: /^edit/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/edit`,
    );
    expect(screen.getByRole("link", { name: /compass/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/compass`,
    );

    expect(document.getElementById("opportunity-overview")).not.toBeNull();
    expect(document.getElementById("opportunity-description")).toBeNull();
    expect(document.getElementById("compass-evaluation")).toBeNull();
  });

  it("renders opportunity application workflow status when tracked", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse(sampleApplication));
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    expect(await screen.findByText("Application workflow")).toBeInTheDocument();
    expect(screen.getByText("interested")).toBeInTheDocument();
    expect(screen.getByText("Search track: Platform search")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open artifacts/i })).toHaveAttribute(
      "href",
      `/applications/${sampleApplication.id}/artifacts`,
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/opportunities/${sampleRole.id}/application`,
      expect.any(Object),
    );
  });

  it("renders a calm empty workflow state when opportunity is not tracked", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404));
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    expect(
      await screen.findByText("Not tracked as an application yet."),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /open artifacts/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /track as application/i }),
    ).toBeInTheDocument();
  });

  it("starts application workflow from the empty state", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse(sampleApplication, 201));
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    await userEvent.click(
      await screen.findByRole("button", { name: /track as application/i }),
    );

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/opportunities/${sampleRole.id}/application`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByText("Application workflow started")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /dismiss notification/i }));
    expect(screen.queryByText("Application workflow started")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open artifacts/i })).toBeInTheDocument();
  });

  it("shows application workflow load errors without hiding opportunity details", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(
        jsonResponse({ detail: "Application workflow unavailable" }, 500),
      );
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    expect(await screen.findByText(sampleRole.title)).toBeInTheDocument();
    expect(
      await screen.findByText("Application workflow unavailable"),
    ).toBeInTheDocument();
  });

  it("re-runs evaluation with force enabled", async () => {
    const user = userEvent.setup();
    const nextEvaluation = {
      ...sampleEvaluation,
      id: "55555555-5555-4555-8555-555555555555",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation))
      .mockResolvedValueOnce(jsonResponse(nextEvaluation, 201));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /re-run evaluation/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/roles/${sampleRole.id}/evaluations`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(JSON.parse(fetchMock.mock.calls[2][1].body as string)).toEqual({
      user_context: {},
      force: true,
    });
  });

  it("shows cached reuse notice when backend returns 200", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation, 200));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Not evaluated")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /run compass evaluation/i }));

    expect(await screen.findByText("Cached COMPASS evaluation reused")).toBeInTheDocument();
  });
});
