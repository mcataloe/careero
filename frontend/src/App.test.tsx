import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { sampleRole } from "./test-data";
import { render, screen } from "./test-utils";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

function renderAppAt(path: string) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("Opportunity routes", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the canonical opportunity list route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse([])));

    renderAppAt("/opportunities");

    expect(await screen.findByRole("heading", { name: "Opportunities" })).toBeInTheDocument();
    expect(screen.getByText("No opportunities yet")).toBeInTheDocument();
  });

  it("renders the canonical add opportunity route", async () => {
    renderAppAt("/opportunities/new");

    expect(screen.getByRole("heading", { name: "Add opportunity" })).toBeInTheDocument();
    expect(screen.getByLabelText(/opportunity title/i)).toBeInTheDocument();
  });

  it("renders the canonical opportunity detail route", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(sampleRole))
        .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404)),
    );

    renderAppAt(`/opportunities/${sampleRole.id}`);

    expect(await screen.findByText("Senior Backend Engineer")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /back to opportunities/i })).toBeInTheDocument();
  });

  it("redirects the legacy roles list route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse([])));

    renderAppAt("/roles");

    expect(await screen.findByRole("heading", { name: "Opportunities" })).toBeInTheDocument();
  });

  it("redirects the legacy add role route", async () => {
    renderAppAt("/roles/new");

    expect(screen.getByRole("heading", { name: "Add opportunity" })).toBeInTheDocument();
  });

  it("redirects the legacy role detail route", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(sampleRole))
        .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404)),
    );

    renderAppAt(`/roles/${sampleRole.id}`);

    expect(await screen.findByText("Senior Backend Engineer")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      `/api/opportunities/${sampleRole.id}`,
      expect.any(Object),
    );
  });
});
