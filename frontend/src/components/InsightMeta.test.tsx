import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import {
  InsightEmptyState,
  InsightListSection,
  InsightRow,
} from "./InsightMeta";
import { render, screen } from "../test-utils";
import type { Insight } from "../types/insights";

const generatedAt = "2026-05-28T15:00:00.000Z";

function insight(overrides: Partial<Insight> = {}): Insight {
  return {
    id: "insight-1",
    category: "risk_red_flag",
    label: "Compensation needs review",
    message: "The stated range is below the search-track target.",
    basis: "Compares parsed opportunity compensation with workspace preferences.",
    confidence: "Weak Signal",
    confidence_level: "weak",
    confidence_explanation: "Only one stated range is available.",
    known_uncertainty: ["Compensation may include equity or bonus not captured here."],
    warnings: ["Review manually before deprioritizing this opportunity."],
    severity: "caution",
    priority: 40,
    generation_method: "deterministic",
    visibility: "internal",
    scope: {
      user_scoped: true,
      workspace_id: "workspace-1",
      opportunity_id: null,
      compass_evaluation_id: null,
      artifact_id: null,
      application_id: null,
    },
    source_references: [
      {
        source_type: "parsed_fields",
        source_id: "role-1",
        label: "Parsed compensation",
        field: "compensation_min",
        metadata: {},
      },
    ],
    source_inputs: { target: 170000, stated: 135000 },
    freshness: {
      generated_at: generatedAt,
      source_updated_at: "2026-05-28T16:00:00.000Z",
      is_stale: true,
      refresh_reason: "Opportunity compensation changed.",
    },
    recommended_action: {
      action_type: "review_compensation",
      label: "Review compensation",
      route_path: "/opportunities/role-1/edit",
      review_required: true,
      metadata: {},
    },
    created_at: null,
    updated_at: null,
    ...overrides,
  };
}

function renderWithRouter(ui: React.ReactNode) {
  render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("InsightMeta shared rendering", () => {
  it("renders hierarchy, provenance, uncertainty, stale state, and routed action", () => {
    renderWithRouter(<InsightRow insight={insight()} />);

    expect(screen.getByText("Compensation needs review")).toBeInTheDocument();
    expect(screen.getByText("caution")).toBeInTheDocument();
    expect(screen.getByLabelText("Severity: caution")).toBeInTheDocument();
    expect(screen.getByText("Priority 40")).toBeInTheDocument();
    expect(screen.getByText("Weak Signal")).toBeInTheDocument();
    expect(screen.getByText("deterministic")).toBeInTheDocument();
    expect(screen.getByText("Search track")).toBeInTheDocument();
    expect(screen.getByText("Stale")).toBeInTheDocument();
    expect(screen.getByText(/Generated May 28, 2026/)).toBeInTheDocument();
    expect(screen.getByText(/source updated May 28, 2026/)).toBeInTheDocument();
    expect(screen.getByText(/Opportunity compensation changed/)).toBeInTheDocument();
    expect(
      screen.getByText("Compares parsed opportunity compensation with workspace preferences."),
    ).toBeInTheDocument();
    expect(screen.getByText("Only one stated range is available.")).toBeInTheDocument();
    expect(
      screen.getByText("Compensation may include equity or bonus not captured here."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Review manually before deprioritizing this opportunity."),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Parsed compensation \(parsed fields: compensation_min\)/),
    ).toBeInTheDocument();

    const link = screen.getByRole("link", { name: /review compensation/i });
    expect(link).toHaveAttribute("href", "/opportunities/role-1/edit");
  });

  it("renders review-required actions without fake links when no route is available", () => {
    renderWithRouter(
      <InsightRow
        insight={insight({
          recommended_action: {
            action_type: "add_note",
            label: "Add decision note",
            route_path: null,
            review_required: true,
            metadata: {},
          },
        })}
      />,
    );

    expect(screen.getByText("Review required: Add decision note")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /add decision note/i })).not.toBeInTheDocument();
  });

  it("renders empty insight sections calmly", () => {
    render(
      <InsightListSection
        insights={[]}
        emptyTitle="No insight yet"
        emptyMessage="Careero will show this after enough tracked data exists."
      />,
    );

    expect(screen.getByText("No insight yet")).toBeInTheDocument();
    expect(
      screen.getByText("Careero will show this after enough tracked data exists."),
    ).toBeInTheDocument();
  });

  it("renders standalone empty states", () => {
    render(
      <InsightEmptyState
        title="No source signal"
        message="Add source metadata to compare private traction."
      />,
    );

    expect(screen.getByText("No source signal")).toBeInTheDocument();
    expect(
      screen.getByText("Add source metadata to compare private traction."),
    ).toBeInTheDocument();
  });
});
