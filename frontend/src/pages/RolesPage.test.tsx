import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RolesPage } from "./RolesPage";
import { sampleEvaluation, sampleRole } from "../test-data";
import { render, screen, waitFor } from "../test-utils";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

function mockFetch(response: unknown, status = 200) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(response, status)));
}

describe("RolesPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders loading and empty states", async () => {
    mockFetch([]);

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Loading opportunities")).toBeInTheDocument();
    expect(await screen.findByText("No opportunities yet")).toBeInTheDocument();
  });

  it("renders an error state", async () => {
    mockFetch({ detail: "Backend unavailable" }, 500);

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });

  it("renders populated roles", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse([sampleRole]))
        .mockResolvedValueOnce(jsonResponse(sampleEvaluation)),
    );

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    await waitFor(() =>
      expect(screen.queryByText("Loading opportunities")).not.toBeInTheDocument(),
    );
    expect(screen.getByText("Senior Backend Engineer")).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("LinkedIn manual")).toBeInTheDocument();
    expect(await screen.findByText("82.00")).toBeInTheDocument();
    expect(screen.getByText("apply")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/opportunities",
      expect.any(Object),
    );
  });

  it("renders not evaluated indicators", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse([sampleRole]))
        .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404)),
    );

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Not evaluated")).toBeInTheDocument();
  });
});
