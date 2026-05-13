import { afterEach, describe, expect, it, vi } from "vitest";

import { RoleForm } from "./RoleForm";
import { fireEvent, render, screen, userEvent, waitFor } from "../test-utils";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

describe("RoleForm", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

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

  it("parses a pasted role, fills empty fields, preserves manual edits, and submits parse metadata", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        parsed: {
          roleTitle: "Parsed Backend Engineer",
          company: "Parsed Company",
          companyWebsite: "https://parsed.example",
          jobUrl: "https://parsed.example/jobs/1",
          source: "linkedin_manual",
          location: "Remote",
          remoteType: "remote",
          compensationMin: 120000,
          compensationMax: 150000,
          currency: "USD",
          datePosted: "2026-05-01",
          normalizedDescription: "Build Python services.",
          extractedSkills: ["Python"],
          warnings: ["Compensation was explicitly present."],
          confidence: { roleTitle: 0.93, company: 0.88 },
        },
        metadata: {
          parserVersion: "role_parser_v1",
          model: "gpt-5-mini",
        },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<RoleForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText(/role title/i), {
      target: { value: "Manual title" },
    });
    fireEvent.change(screen.getByLabelText(/paste job description/i), {
      target: {
        value: "Messy pasted job post with Python and salary $120k-$150k.",
      },
    });
    await user.click(screen.getByRole("button", { name: /parse role/i }));

    expect(await screen.findByText("Parsed role fields")).toBeInTheDocument();
    expect(screen.getByLabelText(/role title/i)).toHaveValue("Manual title");
    expect(screen.getByPlaceholderText("Example Company")).toHaveValue("Parsed Company");
    expect(screen.getByLabelText(/raw description/i)).toHaveValue(
      "Messy pasted job post with Python and salary $120k-$150k.",
    );
    expect(screen.getByText("roleTitle: 93%")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Example Company"), {
      target: { value: "Edited Company" },
    });
    await user.click(screen.getByRole("button", { name: /create role/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Manual title",
        company: {
          name: "Edited Company",
          website_url: "https://parsed.example",
        },
        raw_description: "Messy pasted job post with Python and salary $120k-$150k.",
        normalized_description: "Build Python services.",
        parse_metadata: expect.objectContaining({
          parserVersion: "role_parser_v1",
          aiModel: "gpt-5-mini",
          parseWarnings: ["Compensation was explicitly present."],
          extractedSkills: ["Python"],
          userEditedFields: ["companyName"],
        }),
      }),
    );
  });

  it("keeps manual content when parsing fails", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail: "disabled" }, 503)));

    render(<RoleForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText(/role title/i), {
      target: { value: "Manual title" },
    });
    fireEvent.change(screen.getByPlaceholderText("Example Company"), {
      target: { value: "Manual Company" },
    });
    fireEvent.change(screen.getByLabelText(/paste job description/i), {
      target: { value: "Messy post" },
    });

    await user.click(screen.getByRole("button", { name: /parse role/i }));

    expect(await screen.findByText("Parse failed")).toBeInTheDocument();
    expect(screen.getByLabelText(/role title/i)).toHaveValue("Manual title");
    expect(screen.getByPlaceholderText("Example Company")).toHaveValue("Manual Company");
  });
});
