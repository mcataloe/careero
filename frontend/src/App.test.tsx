import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { sampleRole } from "./test-data";
import { render, screen, userEvent } from "./test-utils";

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
  firstName: "Matthew",
  lastName: "Coleman",
  displayName: "Matthew Coleman",
  salutation: null,
  pronouns: null,
  headshotUrl: null,
  authMethod: "local_password",
  accountStatus: "active",
  createdAt: "2026-05-26T00:00:00Z",
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

  it("opens the floating global navigation from the app header", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse(authUser)).mockResolvedValueOnce(jsonResponse([])),
    );

    renderAppAt("/opportunities");

    expect(await screen.findByRole("heading", { name: "Opportunities" })).toBeInTheDocument();

    await userEvent.click(
      screen.getByRole("button", { name: "Open global navigation" }),
    );

    expect(
      screen.getByRole("navigation", { name: "Global navigation" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /career strategy/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /opportunities/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
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
    expect(screen.getByLabelText(/^email/i)).toBeInTheDocument();
  });
});
