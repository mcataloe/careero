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

const reminders: ApplicationReminder[] = [
  {
    id: "reminder-1",
    application_id: "app-1",
    workspace_id: "workspace-1",
    title: "Follow up with recruiter",
    notes: "Ask for timeline.",
    due_at: "2026-05-15T15:00:00Z",
    completed_at: null,
    reminder_type: "follow_up",
    priority: "high",
    metadata: {},
    created_at: "2026-05-14T15:00:00Z",
    updated_at: "2026-05-14T15:00:00Z",
  },
  {
    id: "reminder-2",
    application_id: "app-1",
    workspace_id: "workspace-1",
    title: "Send thank-you note",
    notes: null,
    due_at: "2026-05-20T15:00:00Z",
    completed_at: "2026-05-20T16:00:00Z",
    reminder_type: "thank_you",
    priority: "normal",
    metadata: {},
    created_at: "2026-05-14T15:00:00Z",
    updated_at: "2026-05-20T16:00:00Z",
  },
];

describe("ApplicationRemindersPanel", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("renders the form and creates a reminder", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.setSystemTime(new Date("2026-05-16T12:00:00Z"));
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(reminders[0], 201));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationRemindersPanel
        applicationId="app-1"
        reminders={[]}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText("No reminders yet.")).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Reminder title"), "Prepare interview");
    await userEvent.clear(screen.getByLabelText("Due date and time"));
    await userEvent.type(screen.getByLabelText("Due date and time"), "2026-05-21T09:30");
    await userEvent.click(screen.getByRole("button", { name: "Add reminder" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/reminders",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          title: "Prepare interview",
          notes: null,
          due_at: new Date("2026-05-21T09:30").toISOString(),
          reminder_type: "follow_up",
          priority: "normal",
          metadata: {},
        }),
      }),
    );
    expect(onChanged).toHaveBeenCalled();
  });

  it("shows overdue state and completes and reopens reminders", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.setSystemTime(new Date("2026-05-16T12:00:00Z"));
    const onChanged = vi.fn().mockResolvedValue(undefined);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ ...reminders[0], completed_at: "2026-05-16T12:00:00Z" }))
      .mockResolvedValueOnce(jsonResponse({ ...reminders[1], completed_at: null }));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ApplicationRemindersPanel
        applicationId="app-1"
        reminders={reminders}
        onChanged={onChanged}
      />,
    );

    expect(screen.getByText("Overdue")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Complete" }));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/applications/app-1/reminders/reminder-1/complete",
      expect.objectContaining({ method: "POST" }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Reopen" }));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/applications/app-1/reminders/reminder-2/reopen",
      expect.objectContaining({ method: "POST" }),
    );
    expect(onChanged).toHaveBeenCalledTimes(2);
  });
});
