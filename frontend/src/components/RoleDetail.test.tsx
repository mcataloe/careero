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
});
