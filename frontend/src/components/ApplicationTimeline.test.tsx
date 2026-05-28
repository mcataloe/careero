import { describe, expect, it } from "vitest";

import { ApplicationTimeline } from "./ApplicationTimeline";
import { render, screen } from "../test-utils";
import type { ApplicationTimelineEvent } from "../types/applications";

const events: ApplicationTimelineEvent[] = [
  {
    id: "state-1",
    application_id: "app-1",
    event_type: "application.state_changed",
    title: "State changed to interested",
    description: "Worth pursuing.",
    occurred_at: "2026-05-16T15:00:00Z",
    actor: "user",
    source_type: "application_state_history",
    source_id: "history-1",
    metadata: {
      from_state: "discovered",
      to_state: "interested",
      recommendation: "apply",
      raw_private_note: { hidden: true },
    },
  },
  {
    id: "created-1",
    application_id: "app-1",
    event_type: "application.created",
    title: "Application tracked",
    description: null,
    occurred_at: "2026-05-15T15:00:00Z",
    actor: "system",
    source_type: "application",
    source_id: "app-1",
    metadata: {},
  },
];

describe("ApplicationTimeline", () => {
  it("renders timeline event labels and metadata", () => {
    render(<ApplicationTimeline events={events} />);

    expect(screen.getByText("State changed to interested")).toBeInTheDocument();
    expect(screen.getByText("Worth pursuing.")).toBeInTheDocument();
    expect(screen.getByText("application state changed")).toBeInTheDocument();
    expect(screen.getByText("To: interested")).toBeInTheDocument();
    expect(screen.getByText("Recommendation: apply")).toBeInTheDocument();
    expect(screen.queryByText(/raw_private_note/i)).not.toBeInTheDocument();
    expect(screen.getByText(/by user/i)).toBeInTheDocument();
  });

  it("renders an empty state", () => {
    render(<ApplicationTimeline events={[]} />);

    expect(screen.getByText("No timeline events recorded yet.")).toBeInTheDocument();
  });
});
