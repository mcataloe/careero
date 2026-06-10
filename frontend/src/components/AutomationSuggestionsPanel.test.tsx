import { describe, expect, it, vi } from "vitest";

import { AutomationSuggestionsPanel } from "./AutomationSuggestionsPanel";
import {
  approveAutomationSuggestion,
  dismissAutomationSuggestion,
} from "../api/automation";
import { render, screen, userEvent, waitFor } from "../test-utils";
import type { AutomationSuggestion } from "../types/automation";

vi.mock("../api/automation", () => ({
  approveAutomationSuggestion: vi.fn().mockResolvedValue({}),
  dismissAutomationSuggestion: vi.fn().mockResolvedValue({}),
  rejectAutomationSuggestion: vi.fn().mockResolvedValue({}),
}));

const suggestion: AutomationSuggestion = {
  id: "suggestion-1",
  workspace_id: "workspace-1",
  target_type: "application",
  target_id: "application-1",
  role_id: "role-1",
  opportunity_id: "role-1",
  application_id: "application-1",
  artifact_id: null,
  action_type: "communication_draft",
  title: "Prepare follow-up draft",
  summary: "A local-only follow-up draft can be reviewed.",
  reason: "Careero can prepare review text without sending it.",
  basis: "Generated from stored application timing only.",
  confidence: "Draft Only",
  source_inputs: {},
  preview: {
    title: "Draft follow-up note",
    body: "Hi, I wanted to briefly follow up.",
    content_hash: "sha256:test",
    external_mutation: false,
  },
  preview_hash: "sha256:test",
  status: "active",
  expires_at: null,
  policy_version: "automation_policy_v1",
  metadata: {},
  created_at: "2026-05-16T15:00:00Z",
  updated_at: "2026-05-16T15:00:00Z",
};

describe("AutomationSuggestionsPanel", () => {
  it("renders suggestion reason, basis, preview, and draft-only boundary", () => {
    render(<AutomationSuggestionsPanel suggestions={[suggestion]} onChanged={vi.fn()} />);

    expect(screen.getByText("Prepare follow-up draft")).toBeInTheDocument();
    expect(screen.getByText("Careero can prepare review text without sending it.")).toBeInTheDocument();
    expect(screen.getByText("Generated from stored application timing only.")).toBeInTheDocument();
    expect(screen.getByText("Hi, I wanted to briefly follow up.")).toBeInTheDocument();
    expect(screen.getByText(/Draft only. Careero will not send this message./i)).toBeInTheDocument();
    expect(screen.getByText("External actions disabled")).toBeInTheDocument();
  });

  it("approves and dismisses through the automation API", async () => {
    const onChanged = vi.fn();
    render(<AutomationSuggestionsPanel suggestions={[suggestion]} onChanged={onChanged} />);

    await userEvent.click(screen.getByRole("button", { name: "Approve log" }));
    await waitFor(() => expect(approveAutomationSuggestion).toHaveBeenCalledWith("suggestion-1"));
    expect(onChanged).toHaveBeenCalledTimes(1);

    await userEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    await waitFor(() => expect(dismissAutomationSuggestion).toHaveBeenCalledWith("suggestion-1"));
  });
});
