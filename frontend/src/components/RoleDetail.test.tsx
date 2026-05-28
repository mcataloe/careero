import { describe, expect, it, vi } from "vitest";

import { RoleDetail } from "./RoleDetail";
import { sampleRole } from "../test-data";
import { render, screen, userEvent, waitFor } from "../test-utils";

describe("RoleDetail", () => {
  it("renders the selected opportunity section and archives from edit", async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const onArchive = vi.fn();

    const { rerender } = render(
      <RoleDetail role={sampleRole} onUpdate={onUpdate} onArchive={onArchive} />,
    );

    expect(screen.getByRole("heading", { name: "Overview" })).toBeInTheDocument();
    expect(screen.getByText("LinkedIn manual")).toBeInTheDocument();
    expect(screen.queryByText("Raw pasted job description")).not.toBeInTheDocument();

    rerender(
      <RoleDetail
        role={sampleRole}
        onUpdate={onUpdate}
        onArchive={onArchive}
        activeSection="edit"
      />,
    );

    await user.click(screen.getByRole("button", { name: /archive opportunity/i }));

    await waitFor(() => expect(onArchive).toHaveBeenCalledTimes(1));
  });

  it("shows clearer intelligence signal confidence and basis", () => {
    const onUpdate = vi.fn();
    const onArchive = vi.fn();
    const roleWithIntelligence = {
      ...sampleRole,
      parse_metadata: {
        opportunityIntelligence: {
          version: "test-v1",
          evaluatedAt: "2026-05-28T15:00:00Z",
          summary: "Stored deterministic caution signals.",
          categories: ["platform"],
          signals: [
            {
              type: "compensation_missing",
              label: "Compensation needs review",
              reason: "The posting did not include a stated range.",
              severity: "medium",
              confidence: "Moderate Confidence",
              basis: "Parsed opportunity fields.",
              evidence: [],
            },
          ],
        },
      },
    };

    render(
      <RoleDetail
        role={roleWithIntelligence}
        onUpdate={onUpdate}
        onArchive={onArchive}
        activeSection="intelligence"
      />,
    );

    expect(screen.getByText("Compensation needs review")).toBeInTheDocument();
    expect(screen.getByText("medium severity")).toBeInTheDocument();
    expect(screen.getByText("Moderate Confidence")).toBeInTheDocument();
    expect(screen.getByText("Parsed opportunity fields.")).toBeInTheDocument();
  });
});
