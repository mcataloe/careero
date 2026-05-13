import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RolesPage } from "./RolesPage";
import { sampleRole } from "../test-data";
import { render, screen, waitFor } from "../test-utils";

function mockFetch(response: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 500,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => response,
    }),
  );
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

    expect(screen.getByText("Loading roles")).toBeInTheDocument();
    expect(await screen.findByText("No roles yet")).toBeInTheDocument();
  });

  it("renders an error state", async () => {
    mockFetch({ detail: "Backend unavailable" }, false);

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });

  it("renders populated roles", async () => {
    mockFetch([sampleRole]);

    render(
      <MemoryRouter>
        <RolesPage />
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.queryByText("Loading roles")).not.toBeInTheDocument());
    expect(screen.getByText("Senior Backend Engineer")).toBeInTheDocument();
    expect(screen.getByText("Example Company")).toBeInTheDocument();
    expect(screen.getByText("LinkedIn manual")).toBeInTheDocument();
  });
});
