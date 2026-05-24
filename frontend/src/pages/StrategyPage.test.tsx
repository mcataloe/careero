import { afterEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";

import { StrategyPage } from "./StrategyPage";
import { render, screen, waitFor } from "../test-utils";
import type { CareerStrategySummary, SearchTrackStrategySummary } from "../types/strategy";
import type { Workspace } from "../types/workspaces";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status >= 200 && status < 300 ? "OK" : "Error",
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const workspace: Workspace = {
  id: "workspace-1",
  user_id: "user-1",
  title: "Full-time search",
  description: null,
  workspace_type: "full_time_individual_contributor",
  status: "active",
  preferences: {},
  ai_context_summary: null,
  tags: [],
  metadata: {},
  archived_at: null,
  created_at: "2026-05-24T12:00:00Z",
  updated_at: "2026-05-24T12:00:00Z",
};

const confidence = {
  confidence: "weak" as const,
  basis: "Sample size is thin.",
  sampleSize: 3,
  sourceInputs: {},
  knownUncertainty: ["Outcome signals are weak."],
  insufficientData: [],
  userOverrides: null,
};

const strategy: SearchTrackStrategySummary = {
  contractVersion: "careero.contracts.v1",
  workspaceId: workspace.id,
  workspaceName: workspace.title,
  generatedAt: "2026-05-24T12:00:00Z",
  summary: "Based on your stored Careero data, this strategy has early evidence.",
  basis: "Derived from workspace-scoped stored records.",
  confidence,
  sampleSize: {
    opportunities: 3,
    applications: 3,
    submittedApplications: 2,
    responses: 1,
    strideEvaluations: 3,
    artifactPerformanceRecords: 0,
  },
  sourceInputs: {},
  knownUncertainty: ["This is not external market data."],
  insufficientData: [
    {
      reason: "missing_artifact_performance",
      message: "No artifact performance records are stored for this track.",
      sourceInputs: {},
    },
  ],
  signals: [
    {
      id: "signal-1",
      category: "search_health",
      label: "High-fit opportunities are producing traction",
      message: "Prioritize similar opportunities before expanding the search.",
      basis: "Stored response and STRIDE data.",
      severity: "positive",
      confidence,
      sourceInputs: {},
    },
  ],
  compensationAlignment: {
    summary: "Stored stated compensation partially overlaps the target.",
    basis: "Internal comparison only.",
    confidence,
    observations: [],
  },
  skillGapThemes: [],
  roleMarketPositioning: {
    summary: "Stored roles appear concentrated around platform.",
    basis: "Title-derived local categories.",
    confidence,
    themes: ["platform"],
  },
  careerNarrativeThemes: [],
  retrospective: {
    summary: "This track has enough evidence for a light retrospective.",
    basis: "Stored workspace evidence.",
    confidence,
    notes: [],
  },
  actionCandidates: [
    {
      id: "review-comp",
      category: "review_compensation_target",
      title: "Review compensation target",
      rationale: "Stored compensation signals suggest review.",
      basis: "Stored stated compensation.",
      confidence,
      sourceInputs: {},
      advisoryOnly: true,
    },
  ],
  warnings: ["Strategy synthesis is read-only."],
};

const careerStrategy: CareerStrategySummary = {
  contractVersion: "careero.contracts.v1",
  generatedAt: "2026-05-24T12:00:00Z",
  summary: "One local track is available.",
  workspaceId: workspace.id,
  workspaceName: workspace.title,
  activeTrack: strategy,
  tracks: [strategy],
  crossTrackComparison: {
    generatedAt: "2026-05-24T12:00:00Z",
    basis: "Compares local search tracks.",
    confidence,
    tracks: [
      {
        workspaceId: workspace.id,
        workspaceName: workspace.title,
        summary: strategy.summary,
        sampleSize: { ...strategy.sampleSize },
        signalCount: 1,
        warningCount: 1,
      },
    ],
    signals: [],
    insufficientData: [],
    warnings: ["This is an internal comparison, not external market data."],
  },
  warnings: [],
};

describe("StrategyPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders workspace strategy synthesis", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse([workspace]))
        .mockResolvedValueOnce(jsonResponse(strategy))
        .mockResolvedValueOnce(jsonResponse(careerStrategy)),
    );

    render(
      <MemoryRouter>
        <StrategyPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Loading strategy synthesis")).toBeInTheDocument();
    expect(await screen.findByText("Career strategy")).toBeInTheDocument();
    expect(screen.getAllByText("Full-time search").length).toBeGreaterThan(0);
    expect(screen.getByText("Review compensation target")).toBeInTheDocument();
    expect(screen.getByText("Cross-track comparison")).toBeInTheDocument();
    expect(screen.getByText("This is not external market data.")).toBeInTheDocument();
  });

  it("requests the selected workspace strategy", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([workspace]))
      .mockResolvedValueOnce(jsonResponse(strategy))
      .mockResolvedValueOnce(jsonResponse(careerStrategy));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <StrategyPage />
      </MemoryRouter>,
    );

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/strategy/workspaces/workspace-1",
        expect.any(Object),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/strategy/workspaces?include_cross_track=true",
      expect.any(Object),
    );
  });
});
