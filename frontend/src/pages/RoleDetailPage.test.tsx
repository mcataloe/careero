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

function renderPage(path = `/opportunities/${sampleRole.id}/compass`) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route
          path="/opportunities/:opportunityId"
          element={<RoleDetailPage />}
        />
        <Route
          path="/opportunities/:opportunityId/:section"
          element={<RoleDetailPage />}
        />
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
      .mockResolvedValueOnce(jsonResponse(sampleRole));
    vi.stubGlobal("fetch", fetchMock);

    renderPage(`/opportunities/${sampleRole.id}/overview`);

    expect(await screen.findByRole("link", { name: /overview/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/overview`,
    );
    expect(screen.getByRole("link", { name: /^description/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/description`,
    );
    expect(screen.getByRole("link", { name: /^edit/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/edit`,
    );
    expect(screen.getByRole("link", { name: /compass/i })).toHaveAttribute(
      "href",
      `/opportunities/${sampleRole.id}/compass`,
    );

    expect(document.getElementById("role-overview")).not.toBeNull();
    expect(document.getElementById("role-description")).toBeNull();
    expect(document.getElementById("compass-evaluation")).toBeNull();
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
