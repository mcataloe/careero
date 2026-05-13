import { describe, expect, it, vi } from "vitest";

import { RoleDetail } from "./RoleDetail";
import { sampleRole } from "../test-data";
import { render, screen, userEvent, waitFor } from "../test-utils";

describe("RoleDetail", () => {
  it("renders role details and archives the role", async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const onArchive = vi.fn();

    render(<RoleDetail role={sampleRole} onUpdate={onUpdate} onArchive={onArchive} />);

    expect(screen.getByRole("heading", { name: "Senior Backend Engineer" })).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("Raw pasted job description")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /archive role/i }));

    await waitFor(() => expect(onArchive).toHaveBeenCalledTimes(1));
  });
});
