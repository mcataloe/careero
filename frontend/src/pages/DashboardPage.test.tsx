import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DashboardPage } from "./DashboardPage";
import { render, screen, waitFor } from "../test-utils";
import type { ApplicationPipelineResponse } from "../types/applications";
import type { CompassInsightsResponse } from "../types/compassInsights";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status >= 200 && status < 300 ? "OK" : "Error",
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const searchAnalytics: SearchAnalyticsResponse = {
  workspace_id: null,
  scope: "all",
  summary: {
    opportunities_saved: {
      value: 4,
      label: "Opportunities saved",
      basis: "Stored opportunities.",
    },
  },
  conversion_rates: [
    {
      from_stage: "applied",
      to_stage: "interviewing",
      numerator: 1,
      denominator: 4,
      rate: 0.25,
      basis: "Tracked applications.",
    },
  ],
  average_stage_durations: [],
  segment_response_rates: [],
  signals: [
    {
      label: "Prioritize active follow-ups",
      confidence: "moderate",
      message: "Some applications have next actions.",
    },
  ],
  insufficient_data: [],
};

const compassInsights: CompassInsightsResponse = {
  workspace_id: null,
  average_compass_score: 82,
  insights: [
    {
      label: "Strong platform fit",
      message: "COMPASS scores are strongest for platform roles.",
      basis: "Stored evaluations.",
      confidence: "moderate",
      severity: "positive",
      source_inputs: {},
    },
  ],
  insufficient_data: [],
};

const workflowPipeline: ApplicationPipelineResponse = {
  workspace_id: null,
  include_inactive: false,
  states: {
    discovered: [],
    interested: [
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
        current_state: "interested",
        applied_at: null,
        next_action_at: "2026-06-01T15:00:00Z",
        updated_at: "2026-05-16T15:00:00Z",
        archived_at: null,
        available_next_states: ["applied", "withdrawn", "archived"],
        compass: null,
        resume_artifact: null,
        cover_letter_artifact: null,
        counts: {
          notes: 0,
          external_links: 0,
          reminders: 1,
          interviews: 0,
        },
      },
    ],
    applied: [],
    interviewing: [],
    offer: [],
    rejected: [],
    withdrawn: [],
  },
};

function renderDashboardAt(path: string) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/dashboard/:section" element={<DashboardPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("DashboardPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads search analytics and workflow attention for the overview route", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(searchAnalytics))
      .mockResolvedValueOnce(jsonResponse(workflowPipeline));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/overview");

    expect(await screen.findByText("Opportunities saved")).toBeInTheDocument();
    expect(screen.getByText("Workflow attention")).toBeInTheDocument();
    expect(screen.getByText("1 active")).toBeInTheDocument();
    expect(screen.getByText("Prioritize active follow-ups")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/analytics/search", expect.any(Object));
    expect(fetchMock).toHaveBeenCalledWith("/api/applications/pipeline", expect.any(Object));
    expect(fetchMock).not.toHaveBeenCalledWith(
      "/api/analytics/compass",
      expect.any(Object),
    );
  });

  it("loads the routed COMPASS dashboard section", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(compassInsights));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/compass");

    expect(await screen.findByText("COMPASS search trends")).toBeInTheDocument();
    expect(screen.getByText("Strong platform fit")).toBeInTheDocument();
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/compass",
        expect.any(Object),
      ),
    );
  });
});
