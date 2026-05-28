import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationNotesPanel } from "./ApplicationNotesPanel";
import { render, screen, userEvent } from "../test-utils";
import type { ApplicationNote } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const notes: ApplicationNote[] = [
  {
    id: "note-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    author: "Local User",
    note_type: "general",
    body: "Initial note",
    created_at: "2026-05-16T15:00:00Z",
    updated_at: "2026-05-16T15:00:00Z",
  },
];

describe("ApplicationNotesPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders an empty state and creates a note", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ ...notes[0], body: "Created note" }, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationNotesPanel
        applicationId="app-1"
        notes={[]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText(/No notes yet/)).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("New note"), "Created note");
    await userEvent.click(screen.getByRole("button", { name: "Add note" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/notes",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ body: "Created note", note_type: "general" }),
      }),
    );
    expect(onChanged).toHaveBeenCalled();
  });

  it("edits and deletes notes", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ ...notes[0], body: "Updated note" }))
      .mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers(),
        text: async () => "",
      });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationNotesPanel
        applicationId="app-1"
        notes={notes}
        onChanged={onChanged}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    await userEvent.clear(screen.getByLabelText("Edit note"));
    await userEvent.type(screen.getByLabelText("Edit note"), "Updated note");
    await userEvent.click(screen.getByRole("button", { name: "Save note" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/notes/note-1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ body: "Updated note", note_type: "general" }),
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/applications/app-1/notes/note-1",
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(onChanged).toHaveBeenCalledTimes(2);
  });
});
