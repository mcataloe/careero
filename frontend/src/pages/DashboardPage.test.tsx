import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DashboardPage } from "./DashboardPage";
import { render, screen, userEvent, waitFor } from "../test-utils";
import type { ApplicationPipelineResponse } from "../types/applications";
import type { ArtifactPerformanceResponse } from "../types/artifactPerformance";
import type { CompensationIntelligenceResponse } from "../types/compensationIntelligence";
import type { CompassInsightsResponse } from "../types/compassInsights";
import type { RecommendationListResponse } from "../types/recommendations";
import type { Insight } from "../types/insights";
import type { SearchAnalyticsResponse } from "../types/searchAnalytics";
import type { SourceIntelligenceResponse } from "../types/sourceIntelligence";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status >= 200 && status < 300 ? "OK" : "Error",
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const generatedAt = "2026-05-28T15:00:00.000Z";

function insight(overrides: Partial<Insight>): Insight {
  return {
    id: "insight-test",
    category: "other",
    label: "Insight",
    message: "Insight message.",
    basis: "Stored Careero data.",
    confidence: "Weak Signal",
    confidence_level: "weak",
    confidence_explanation: null,
    known_uncertainty: ["Outcome history is still thin."],
    warnings: [],
    severity: "info",
    priority: null,
    generation_method: "deterministic",
    visibility: "internal",
    scope: {
      user_scoped: true,
      workspace_id: null,
      opportunity_id: null,
      compass_evaluation_id: null,
      artifact_id: null,
      application_id: null,
    },
    source_references: [],
    source_inputs: {},
    freshness: {
      generated_at: generatedAt,
      source_updated_at: null,
      is_stale: false,
      refresh_reason: null,
    },
    recommended_action: null,
    created_at: null,
    updated_at: null,
    ...overrides,
  };
}

const searchAnalytics: SearchAnalyticsResponse = {
  generated_at: generatedAt,
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
    insight({
      label: "Prioritize active follow-ups",
      confidence: "Moderate Confidence",
      confidence_level: "moderate",
      message: "Some applications have next actions.",
    }),
  ],
  insufficient_data: [],
};

const compassInsights: CompassInsightsResponse = {
  generated_at: generatedAt,
  workspace_id: null,
  average_compass_score: 82,
  insights: [
    insight({
      id: "compass-insight",
      category: "compass",
      label: "Strong platform fit",
      message: "COMPASS scores are strongest for platform roles.",
      basis: "Stored evaluations.",
      confidence: "Moderate Confidence",
      confidence_level: "moderate",
      severity: "positive",
      source_inputs: {},
    }),
  ],
  insufficient_data: [],
};

const sourceIntelligence: SourceIntelligenceResponse = {
  generated_at: generatedAt,
  workspace_id: null,
  summaries: [
    {
      source_type: "recruiter",
      label: "Recruiter",
      opportunities: 2,
      applications: 2,
      responses: 1,
      interviews: 1,
      response_rate: 0.5,
      interview_rate: 0.5,
      average_compass_score: 82,
      recruiter_contacts: 2,
      compensation_aligned: 1,
      basis: "Tracked source metadata.",
    },
  ],
  insights: [
    insight({
      id: "source-insight",
      category: "source_intelligence",
      label: "Recruiter channel is getting traction",
      message: "Recruiter-sourced opportunities are producing responses.",
      basis: "Compared tracked source outcomes.",
      source_references: [
        {
          source_type: "workspace",
          source_id: null,
          label: "All tracked opportunities",
          field: "source_type",
          metadata: {},
        },
      ],
    }),
  ],
  insufficient_data: [],
};

const artifactPerformance: ArtifactPerformanceResponse = {
  generated_at: generatedAt,
  workspace_id: null,
  summary: [],
  by_role_category: [],
  by_variant: [
    {
      label: "Platform resume",
      artifact_type: "resume",
      variant_name: "Platform resume",
      role_category: "platform",
      total: 2,
      responses: 1,
      interviews: 1,
      response_rate: 0.5,
      interview_rate: 0.5,
      basis: "Observed application outcomes.",
    },
  ],
  insights: [
    insight({
      id: "artifact-insight",
      category: "artifact_readiness",
      label: "Platform resume has early signal",
      message: "The platform resume variant has one observed response.",
      basis: "Compared artifact usage with tracked outcomes.",
    }),
  ],
  insufficient_data: [],
};

const recommendations: RecommendationListResponse = {
  generated_at: generatedAt,
  workspace_id: null,
  read_only: true,
  recommendations: [
    {
      ...insight({
        id: "recommendation-insight",
        category: "follow_up_action",
        label: "Review COMPASS evaluation",
        message: "Revisit the latest COMPASS rationale before tailoring.",
        basis: "Latest evaluation has moderate confidence.",
        recommended_action: {
          action_type: "review_compass",
          label: "Review COMPASS",
          route_path: "/opportunities/role-1/compass",
          review_required: true,
          metadata: {},
        },
      }),
      recommendation_type: "compass_review",
      subject_type: "opportunity",
      subject_id: "role-1",
      action: "review_compass",
      title: "Review COMPASS evaluation",
      reason: "Latest evaluation has moderate confidence.",
    },
  ],
};

const emptyCompensation: CompensationIntelligenceResponse = {
  generated_at: generatedAt,
  workspace_id: null,
  target_compensation_min: null,
  observations: [],
  insights: [],
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

  it("shows loading state while a dashboard section is pending", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));

    renderDashboardAt("/dashboard/overview");

    expect(screen.getByText("Loading search overview")).toBeInTheDocument();
  });

  it("shows recoverable error state for failed insight requests", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "Insight request failed" }, 500))
      .mockResolvedValueOnce(jsonResponse(workflowPipeline));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/overview");

    expect(await screen.findByText("Insight request failed")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
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
    expect(screen.getAllByText("Moderate Confidence")[0]).toBeInTheDocument();
    expect(screen.getByText(/Generated May 28, 2026/)).toBeInTheDocument();
    expect(screen.getByText("Outcome history is still thin.")).toBeInTheDocument();
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
    expect(screen.getByText("positive")).toBeInTheDocument();
    expect(screen.getByText("All workspaces")).toBeInTheDocument();
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/compass",
        expect.any(Object),
      ),
    );
  });

  it("shows source insight messages alongside source metrics", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(sourceIntelligence));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/sources");

    expect(
      await screen.findByText("Recruiter channel is getting traction"),
    ).toBeInTheDocument();
    expect(screen.getByText("Recruiter")).toBeInTheDocument();
    expect(screen.getByText("Compared tracked source outcomes.")).toBeInTheDocument();
    expect(screen.getByText(/All tracked opportunities/)).toBeInTheDocument();
  });

  it("shows artifact insight messages alongside artifact metrics", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(artifactPerformance));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/artifacts");

    expect(await screen.findByText("Platform resume has early signal")).toBeInTheDocument();
    expect(screen.getByText("Platform resume")).toBeInTheDocument();
    expect(
      screen.getByText("Compared artifact usage with tracked outcomes."),
    ).toBeInTheDocument();
  });

  it("renders recommended actions as route links when available", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(recommendations));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/recommendations");

    expect(await screen.findByText("Review COMPASS evaluation")).toBeInTheDocument();
    const link = screen.getByRole("link", { name: /review compass/i });
    expect(link).toHaveAttribute("href", "/opportunities/role-1/compass");
  });

  it("renders calm empty states for insight sections", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(emptyCompensation));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/compensation");

    expect(await screen.findByText("No compensation insight yet")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Add stated compensation ranges to saved opportunities to compare against search-track targets.",
      ),
    ).toBeInTheDocument();
  });

  it("reloads section data when a dashboard submenu item is clicked", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(searchAnalytics))
      .mockResolvedValueOnce(jsonResponse(workflowPipeline))
      .mockResolvedValueOnce(jsonResponse(compassInsights));
    vi.stubGlobal("fetch", fetchMock);

    renderDashboardAt("/dashboard/overview");

    expect(await screen.findByText("Workflow attention")).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: /compass/i }));

    expect(await screen.findByText("COMPASS search trends")).toBeInTheDocument();
    expect(screen.getByText("Strong platform fit")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/analytics/compass",
      expect.any(Object),
    );
  });
});
