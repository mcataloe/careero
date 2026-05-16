import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationLinksPanel } from "./ApplicationLinksPanel";
import { render, screen, userEvent } from "../test-utils";
import type { ApplicationExternalLink } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const links: ApplicationExternalLink[] = [
  {
    id: "link-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    label: "Job posting",
    url: "https://example.com/jobs/1",
    type: "job_posting",
    metadata: {},
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

describe("ApplicationLinksPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders safe outbound links and creates a link", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(links[0], 201));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationLinksPanel
        applicationId="app-1"
        links={links}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByRole("link", { name: "Job posting" })).toHaveAttribute(
      "target",
      "_blank",
    );
    expect(screen.getByRole("link", { name: "Job posting" })).toHaveAttribute(
      "rel",
      "noreferrer noopener",
    );

    await userEvent.type(screen.getByLabelText("Label"), "Application portal");
    await userEvent.type(screen.getByLabelText("URL"), "https://example.com/portal");
    await userEvent.click(screen.getByRole("button", { name: "Add link" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/links",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          label: "Application portal",
          url: "https://example.com/portal",
          type: "other",
        }),
      }),
    );
    expect(onChanged).toHaveBeenCalled();
  });

  it("renders an empty state and edits and deletes links", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ ...links[0], label: "Portal" }))
      .mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers(),
        text: async () => "",
      });
    vi.stubGlobal("fetch", fetchMock);

    const { rerender } = render(
      <ApplicationLinksPanel
        applicationId="app-1"
        links={[]}
        onChanged={onChanged}
      />,
    );
    expect(screen.getByText("No external links yet.")).toBeInTheDocument();

    rerender(
      <ApplicationLinksPanel
        applicationId="app-1"
        links={links}
        onChanged={onChanged}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    await userEvent.clear(screen.getAllByLabelText("Label")[1]);
    await userEvent.type(screen.getAllByLabelText("Label")[1], "Portal");
    await userEvent.click(screen.getByRole("button", { name: "Save link" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/links/link-1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          label: "Portal",
          url: "https://example.com/jobs/1",
          type: "job_posting",
        }),
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/applications/app-1/links/link-1",
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(onChanged).toHaveBeenCalledTimes(2);
  });
});
