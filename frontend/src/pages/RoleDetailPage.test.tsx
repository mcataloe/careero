import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RoleDetailPage } from "./RoleDetailPage";
import { sampleEvaluation, sampleRole } from "../test-data";
import { render, screen, userEvent, waitFor } from "../test-utils";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

function renderPage() {
  render(
    <MemoryRouter initialEntries={[`/opportunities/${sampleRole.id}`]}>
      <Routes>
        <Route path="/opportunities/:opportunityId" element={<RoleDetailPage />} />
        <Route path="/opportunities" element={<div>Opportunities</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RoleDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("runs evaluation from a not-evaluated role and displays the result", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation, 201));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Not evaluated")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/opportunities/${sampleRole.id}`,
      expect.any(Object),
    );
    await user.click(screen.getByRole("button", { name: /run compass evaluation/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/roles/${sampleRole.id}/evaluations`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(JSON.parse(fetchMock.mock.calls[2][1].body as string)).toEqual({
      user_context: {},
    });
    expect(await screen.findByText("COMPASS evaluation completed")).toBeInTheDocument();
    expect(screen.getByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
  });

  it("renders section navigation with valid role detail targets", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByRole("link", { name: /overview/i })).toHaveAttribute(
      "href",
      "#role-overview",
    );
    expect(screen.getByRole("link", { name: /^description$/i })).toHaveAttribute(
      "href",
      "#role-description",
    );
    expect(
      screen.getByRole("link", { name: /normalized description/i }),
    ).toHaveAttribute("href", "#role-normalized-description");
    expect(screen.getByRole("link", { name: /edit opportunity/i })).toHaveAttribute(
      "href",
      "#role-edit",
    );
    expect(
      screen.getByRole("link", { name: /compass evaluation/i }),
    ).toHaveAttribute("href", "#compass-evaluation");
    expect(screen.getByRole("link", { name: /^summary$/i })).toHaveAttribute(
      "href",
      "#compass-summary",
    );
    expect(screen.getByRole("link", { name: /ats findings/i })).toHaveAttribute(
      "href",
      "#compass-ats-findings",
    );

    expect(document.getElementById("role-overview")).not.toBeNull();
    expect(document.getElementById("role-description")).not.toBeNull();
    expect(document.getElementById("role-normalized-description")).not.toBeNull();
    expect(document.getElementById("role-edit")).not.toBeNull();
    expect(document.getElementById("compass-evaluation")).not.toBeNull();
    expect(document.getElementById("compass-summary")).not.toBeNull();
    expect(document.getElementById("compass-ats-findings")).not.toBeNull();
  });

  it("re-runs evaluation with force enabled", async () => {
    const user = userEvent.setup();
    const nextEvaluation = {
      ...sampleEvaluation,
      id: "55555555-5555-4555-8555-555555555555",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation))
      .mockResolvedValueOnce(jsonResponse(nextEvaluation, 201));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /re-run evaluation/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/roles/${sampleRole.id}/evaluations`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(JSON.parse(fetchMock.mock.calls[2][1].body as string)).toEqual({
      user_context: {},
      force: true,
    });
  });

  it("shows cached reuse notice when backend returns 200", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(sampleRole))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse(sampleEvaluation, 200));
    vi.stubGlobal("fetch", fetchMock);

    renderPage();

    expect(await screen.findByText("Not evaluated")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /run compass evaluation/i }));

    expect(await screen.findByText("Cached COMPASS evaluation reused")).toBeInTheDocument();
  });
});
