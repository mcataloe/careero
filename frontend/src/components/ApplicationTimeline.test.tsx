import { describe, it, expect } from "vitest";
import { render, screen } from "../../test-utils";
import { ApplicationTimeline } from "./ApplicationTimeline";
import { TimelineEvent } from "../types/timeline";

describe("ApplicationTimeline", () => {
  it("renders empty state gracefully", () => {
    render(<ApplicationTimeline events={[]} />);
    expect(
      screen.getByText(/no timeline events recorded yet/i),
    ).toBeInTheDocument();
  });

  it("renders a list of typed events", () => {
    const mockEvents: TimelineEvent[] = [
      {
        id: "event-1",
        applicationId: "app-1",
        eventType: "application.state_changed",
        title: "Moved to Interviewing",
        description: "Scheduled first round",
        occurredAt: new Date().toISOString(),
        actor: "user",
        sourceType: "application_state_history",
        sourceId: "history-1",
      },
      {
        id: "event-2",
        applicationId: "app-1",
        eventType: "application.created",
        title: "Application tracked",
        occurredAt: new Date(Date.now() - 86400000).toISOString(),
        actor: "system",
        sourceType: "application",
        sourceId: "app-1",
      },
    ];

    render(<ApplicationTimeline events={mockEvents} />);
    expect(screen.getByText("Moved to Interviewing")).toBeInTheDocument();
    expect(screen.getByText("Scheduled first round")).toBeInTheDocument();
    expect(screen.getByText("Application tracked")).toBeInTheDocument();
  });
});
