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

const authUser = {
  id: "user-1",
  email: "matthew@example.com",
  first_name: "Matthew",
  last_name: "Coleman",
  display_name: "Matthew Coleman",
  auth_method: "local_password",
  account_status: "active",
  created_at: "2026-05-26T00:00:00Z",
};

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
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse(authUser)).mockResolvedValueOnce(jsonResponse([])),
    );

    renderAppAt("/opportunities");

    expect(await screen.findByRole("heading", { name: "Opportunities" })).toBeInTheDocument();
    expect(await screen.findByText("No opportunities yet")).toBeInTheDocument();
  });

  it("renders the canonical add opportunity route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse(authUser)));

    renderAppAt("/opportunities/new");

    expect(await screen.findByRole("heading", { name: "Add opportunity" })).toBeInTheDocument();
    expect(screen.getByLabelText(/opportunity title/i)).toBeInTheDocument();
  });

  it("renders the canonical opportunity detail route", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(authUser))
        .mockResolvedValueOnce(jsonResponse(sampleRole))
        .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404)),
    );

    renderAppAt(`/opportunities/${sampleRole.id}`);

    expect(await screen.findByText("Senior Backend Engineer")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /back to opportunities/i })).toBeInTheDocument();
  });

  it("redirects the legacy roles list route", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse(authUser)).mockResolvedValueOnce(jsonResponse([])),
    );

    renderAppAt("/roles");

    expect(await screen.findByRole("heading", { name: "Opportunities" })).toBeInTheDocument();
  });

  it("redirects the legacy add role route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse(authUser)));

    renderAppAt("/roles/new");

    expect(await screen.findByRole("heading", { name: "Add opportunity" })).toBeInTheDocument();
  });

  it("redirects the legacy role detail route", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(authUser))
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

  it("redirects unauthenticated app routes to login", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse({ detail: "Authentication required" }, 401)));

    renderAppAt("/dashboard");

    expect(await screen.findByRole("heading", { name: "Careero" })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });
});
