import { describe, expect, it, vi } from "vitest";

import { StrideEvaluationDetail } from "./StrideEvaluationDetail";
import { sampleEvaluation } from "../test-data";
import { render, screen, userEvent, waitFor } from "../test-utils";

describe("StrideEvaluationDetail", () => {
  it("renders completed evaluation details and unsupported warnings", () => {
    render(
      <StrideEvaluationDetail
        evaluation={sampleEvaluation}
        onRun={vi.fn()}
        onViewLatest={vi.fn()}
      />,
    );

    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getAllByText("apply").length).toBeGreaterThan(0);
    expect(screen.getAllByText("medium").length).toBeGreaterThan(0);
    expect(screen.getByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
    expect(screen.getByText("Python and PostgreSQL are explicit role signals.")).toBeInTheDocument();
    expect(screen.getByText("kubernetes")).toBeInTheDocument();
    expect(screen.getByText("Do not claim Kubernetes experience without source evidence.")).toBeInTheDocument();
    expect(screen.getByText(/AI fallback: AI evaluations are disabled/i)).toBeInTheDocument();
    expect(document.getElementById("stride-summary")).not.toBeNull();
    expect(document.getElementById("stride-fit-analysis")).not.toBeNull();
    expect(document.getElementById("stride-ats-findings")).not.toBeNull();
    expect(document.getElementById("stride-interview-positioning")).not.toBeNull();
  });

  it("renders not evaluated state and runs evaluation", async () => {
    const user = userEvent.setup();
    const onRun = vi.fn();

    render(<StrideEvaluationDetail evaluation={null} onRun={onRun} />);

    expect(screen.getByText("Not evaluated")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /run stride evaluation/i }));

    await waitFor(() => expect(onRun).toHaveBeenCalledWith(false));
  });

  it("sends force flag for re-run action", async () => {
    const user = userEvent.setup();
    const onRun = vi.fn();

    render(<StrideEvaluationDetail evaluation={sampleEvaluation} onRun={onRun} />);

    await user.click(screen.getByRole("button", { name: /re-run evaluation/i }));

    await waitFor(() => expect(onRun).toHaveBeenCalledWith(true));
  });

  it("renders top-level AI failure metadata safely", () => {
    render(
      <StrideEvaluationDetail
        evaluation={{
          ...sampleEvaluation,
          ai_status: "failed",
          error_message: "timeout for sk-REDACTED",
          raw_evaluation_json: {},
        }}
        onRun={vi.fn()}
      />,
    );

    expect(screen.getAllByText("AI failed").length).toBeGreaterThan(0);
    expect(screen.getByText(/timeout for sk-REDACTED/i)).toBeInTheDocument();
  });

  it("renders validation-failed state without treating it as completed", () => {
    render(
      <StrideEvaluationDetail
        evaluation={{
          ...sampleEvaluation,
          evaluation_status: "failed",
          raw_evaluation_json: {
            validationIssues: [{ message: "summary is required" }],
          },
        }}
        onRun={vi.fn()}
      />,
    );

    expect(screen.getAllByText("Validation failed").length).toBeGreaterThan(0);
    expect(screen.getByText("summary is required")).toBeInTheDocument();
  });

  it("renders long canonical-style sections with progressive disclosure", () => {
    const longSummary = Array.from({ length: 24 }, (_, index) => `Line ${index + 1}`).join("\n");

    render(
      <StrideEvaluationDetail
        evaluation={{
          ...sampleEvaluation,
          summary: longSummary,
          overallScore: 91,
          overall_score: undefined,
          recommendation: undefined,
          recommendations: {
            decision: "monitor",
            rationale: "Review fit before applying.",
            nextActions: ["Prepare concise leadership examples"],
          },
          confidence: {
            level: "high",
            score: 0.88,
            rationale: "Role content and resume source are both available.",
          },
          sections: {
            strategicFit: {
              status: "strong_match",
              score: 90,
              summary: "Workspace preferences align with the opportunity.",
              evidence: ["Platform leadership"],
              gaps: [],
              assumptions: [],
            },
          },
          assumptions: ["No external research was used."],
        }}
        onRun={vi.fn()}
      />,
    );

    expect(screen.getByText("91")).toBeInTheDocument();
    expect(screen.getAllByText("monitor").length).toBeGreaterThan(0);
    expect(screen.getByText("Workspace preferences align with the opportunity.")).toBeInTheDocument();
    expect(screen.getByText("Prepare concise leadership examples")).toBeInTheDocument();
    expect(screen.getByText(/Line 24/)).toBeInTheDocument();
  });
});
