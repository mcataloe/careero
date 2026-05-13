import { afterEach, describe, expect, it, vi } from "vitest";

import { ResumeSourceSettings } from "./ResumeSourceSettings";
import { render, screen, userEvent, waitFor } from "../test-utils";

function jsonResponse(data: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => data,
  };
}

const activeSource = {
  source: {
    id: "source-1",
    name: "Master Resume",
    source_type: "master_resume",
    created_at: "2026-05-13T12:00:00Z",
    updated_at: "2026-05-13T12:00:00Z",
    latest_version: null,
    active_version: null,
  },
  version: {
    id: "version-1",
    source_id: "source-1",
    version_label: "v1",
    raw_text: "Python backend engineer",
    normalized_summary: "Backend engineer",
    is_active: true,
    created_at: "2026-05-13T12:00:00Z",
    updated_at: "2026-05-13T12:00:00Z",
  },
};

describe("ResumeSourceSettings", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("handles empty state and creates active source", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "Not found" }, 404))
      .mockResolvedValueOnce(jsonResponse({ id: "source-1" }, 201))
      .mockResolvedValueOnce(jsonResponse(activeSource));
    vi.stubGlobal("fetch", fetchMock);

    render(<ResumeSourceSettings />);

    expect(await screen.findByText("No active source")).toBeInTheDocument();
    await user.type(screen.getByLabelText(/raw resume\/profile text/i), "Python backend engineer");
    await user.click(screen.getByRole("button", { name: /create active source/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      "/api/resume-sources",
      expect.objectContaining({ method: "POST" }),
    ));
    expect(await screen.findByText("Active resume source created")).toBeInTheDocument();
  });

  it("loads active source and creates an active replacement version", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(activeSource))
      .mockResolvedValueOnce(jsonResponse({ ...activeSource.version, id: "version-2" }, 201))
      .mockResolvedValueOnce(jsonResponse({ ...activeSource.version, id: "version-2" }))
      .mockResolvedValueOnce(jsonResponse(activeSource));
    vi.stubGlobal("fetch", fetchMock);

    render(<ResumeSourceSettings />);

    expect(await screen.findByText(/active version: v1/i)).toBeInTheDocument();
    await user.clear(screen.getByLabelText(/new version label/i));
    await user.type(screen.getByLabelText(/new version label/i), "v2");
    await user.click(screen.getByRole("button", { name: /save active version/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      "/api/resume-sources/source-1/versions",
      expect.objectContaining({ method: "POST" }),
    ));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      "/api/resume-sources/source-1/versions/version-2/activate",
      expect.objectContaining({ method: "POST" }),
    ));
  });

  it("renders load errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "Backend unavailable" }, 500)),
    );

    render(<ResumeSourceSettings />);

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });
});
