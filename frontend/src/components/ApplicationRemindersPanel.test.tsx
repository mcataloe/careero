import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationRemindersPanel } from "./ApplicationRemindersPanel";
import { render, screen, userEvent } from "../test-utils";
import type { ApplicationReminder } from "../types/applications";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const reminder: ApplicationReminder = {
  id: "reminder-1",
  application_id: "app-1",
  workspace_id: "workspace-1",
  title: "Follow up",
  due_at: "2026-05-20T15:00:00Z",
  notes: "Ask about next steps.",
  completed_at: null,
  created_at: "2026-05-16T15:00:00Z",
  updated_at: "2026-05-16T15:00:00Z",
};

describe("ApplicationRemindersPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders empty state and creates a reminder", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(reminder, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationRemindersPanel
        applicationId="app-1"
        reminders={[]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText(/No reminders yet/)).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("Reminder title"), "Follow up");
    await userEvent.type(screen.getByLabelText("Due date"), "2026-05-20T10:00");
    await userEvent.type(screen.getByLabelText("Reminder notes"), "Ask next steps.");
    await userEvent.click(screen.getByRole("button", { name: "Add reminder" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/reminders",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining('"title":"Follow up"'),
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/reminders",
      expect.objectContaining({
        body: expect.stringContaining('"notes":"Ask next steps."'),
      }),
    );
    expect(onChanged).toHaveBeenCalled();
  });

  it("edits and completes reminders", async () => {
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ ...reminder, title: "Updated follow up" }))
      .mockResolvedValueOnce(
        jsonResponse({
          ...reminder,
          completed_at: "2026-05-20T16:00:00Z",
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationRemindersPanel
        applicationId="app-1"
        reminders={[reminder]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText("Follow up")).toBeInTheDocument();
    expect(screen.getByText("Ask about next steps.")).toBeInTheDocument();
    expect(screen.getByText("Overdue")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    await userEvent.clear(screen.getByLabelText("Edit reminder title"));
    await userEvent.type(
      screen.getByLabelText("Edit reminder title"),
      "Updated follow up",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save reminder" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/reminders/reminder-1",
      expect.objectContaining({
        method: "PATCH",
        body: expect.stringContaining('"title":"Updated follow up"'),
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Complete" }));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/applications/app-1/reminders/reminder-1/complete",
      expect.objectContaining({ method: "POST" }),
    );
    expect(onChanged).toHaveBeenCalledTimes(2);
  });
});
