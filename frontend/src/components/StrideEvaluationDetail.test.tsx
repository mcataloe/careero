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
    expect(screen.getByText("apply")).toBeInTheDocument();
    expect(screen.getAllByText("medium").length).toBeGreaterThan(0);
    expect(screen.getByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
    expect(screen.getByText("Python and PostgreSQL are explicit role signals.")).toBeInTheDocument();
    expect(screen.getByText("kubernetes")).toBeInTheDocument();
    expect(screen.getByText("Do not claim Kubernetes experience without source evidence.")).toBeInTheDocument();
    expect(screen.getByText(/AI fallback: AI evaluations are disabled/i)).toBeInTheDocument();
  });

  it("renders not evaluated state and runs evaluation", async () => {
    const user = userEvent.setup();
    const onRun = vi.fn();

    render(<StrideEvaluationDetail evaluation={null} onRun={onRun} />);

    expect(screen.getByText("Not evaluated")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /run stride evaluation/i }));

    await waitFor(() => expect(onRun).toHaveBeenCalledTimes(1));
  });
});
