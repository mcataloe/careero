import { describe, expect, it, vi } from "vitest";

import { RoleForm } from "./RoleForm";
import { fireEvent, render, screen, userEvent, waitFor } from "../test-utils";

describe("RoleForm", () => {
  it("validates required fields and submits the expected payload", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<RoleForm onSubmit={onSubmit} />);

    await user.click(screen.getByRole("button", { name: /create role/i }));

    expect(await screen.findByText("Title is required")).toBeInTheDocument();
    expect(screen.getByText("Company is required")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText(/role title/i), {
      target: { value: "Senior Backend Engineer" },
    });
    fireEvent.change(screen.getByPlaceholderText("Example Company"), {
      target: { value: "Example Company" },
    });
    fireEvent.change(screen.getByLabelText(/job url/i), {
      target: { value: "https://www.linkedin.com/jobs/view/example" },
    });
    await user.click(screen.getByRole("button", { name: /create role/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Senior Backend Engineer",
        company: {
          name: "Example Company",
          website_url: null,
        },
        source: { source_type: "manual" },
        job_url: "https://www.linkedin.com/jobs/view/example",
        status: "found",
      }),
    );
  });
});
