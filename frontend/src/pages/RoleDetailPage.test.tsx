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
    <MemoryRouter initialEntries={[`/roles/${sampleRole.id}`]}>
      <Routes>
        <Route path="/roles/:roleId" element={<RoleDetailPage />} />
        <Route path="/roles" element={<div>Roles</div>} />
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
    await user.click(screen.getByRole("button", { name: /run stride evaluation/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `/api/roles/${sampleRole.id}/evaluations`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByText("STRIDE evaluation completed")).toBeInTheDocument();
    expect(screen.getByText("Strong baseline fit for backend platform work.")).toBeInTheDocument();
  });
});
