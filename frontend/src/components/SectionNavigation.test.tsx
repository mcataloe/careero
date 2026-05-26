import { afterEach, describe, expect, it, vi } from "vitest";

import { SectionNavigation } from "./SectionNavigation";
import { render, screen, userEvent, waitFor } from "../test-utils";

describe("SectionNavigation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders anchor-style section links and scrolls to the target", async () => {
    const user = userEvent.setup();
    const scrollIntoView = vi.fn();
    const target = document.createElement("div");
    target.id = "compass-evaluation";
    target.scrollIntoView = scrollIntoView;
    document.body.appendChild(target);

    render(
      <SectionNavigation
        items={[{ label: "COMPASS Evaluation", targetId: "compass-evaluation" }]}
      />,
    );

    const link = screen.getByRole("link", { name: /compass evaluation/i });
    expect(link).toHaveAttribute("href", "#compass-evaluation");

    await user.click(link);

    await waitFor(() =>
      expect(scrollIntoView).toHaveBeenCalledWith({
        behavior: "smooth",
        block: "start",
      }),
    );
  });
});
