import { afterEach, describe, expect, it, vi } from "vitest";
import userEvent from "@testing-library/user-event";

vi.mock("../components/AutomationPreferencesPanel", () => ({
  AutomationPreferencesPanel: () => <div>Automation settings placeholder</div>,
}));

vi.mock("../components/ResumeSourceSettings", () => ({
  ResumeSourceSettings: () => <div>Resume source settings placeholder</div>,
}));

import { SettingsPage } from "./SettingsPage";
import { render, screen } from "../test-utils";
import type { ProductizationReadiness } from "../types/productization";

function jsonResponse(data: unknown) {
  return {
    ok: true,
    status: 200,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => data,
  };
}

const readiness: ProductizationReadiness = {
  environment: "local",
  readiness_stage: "local_poc",
  production_ready: false,
  local_first_status: "active_local_first",
  local_workflow_readiness: {
    core_workflow: { status: "local_available", implemented: true, detail: "" },
    application_workflow: { status: "local_available", implemented: true, detail: "" },
    artifact_lifecycle: { status: "incomplete", implemented: false, detail: "" },
    integrations: { status: "local_only", implemented: false, detail: "" },
    automation: { status: "local_guardrails_only", implemented: true, detail: "" },
  },
  database_health: "available",
  ai_feature_flags: {
    role_parsing_enabled: false,
    compass_enrichment_enabled: false,
    resume_generation_enabled: false,
    cover_letter_generation_enabled: false,
    provider_key_configured: false,
    local_session_attempt_cap: 25,
    durable_metering_status: "not_implemented",
  },
  auth_status: { status: "not_implemented", implemented: false, detail: "" },
  tenant_boundary_prep_status: {
    status: "local_boundary_prep",
    implemented: true,
    detail: "",
  },
  billing_status: { status: "not_implemented", implemented: false, detail: "" },
  export_delete_status: { status: "local_export_available", implemented: true, detail: "" },
  retention_status: { status: "not_enforced", implemented: false, detail: "" },
  durable_usage_metering_status: {
    status: "not_implemented",
    implemented: false,
    detail: "",
  },
  deployment_status: { status: "local_only", implemented: true, detail: "" },
  hosted_collaboration_status: {
    status: "not_implemented",
    implemented: false,
    detail: "",
  },
  marketplace_employer_side_status: {
    status: "not_implemented",
    implemented: false,
    detail: "",
  },
  known_blockers: ["Production authentication is not implemented."],
  production_readiness_statement:
    "Careero is not production-ready unless all required productization gates pass.",
};

describe("SettingsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the product readiness panel", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse(readiness)));

    render(<SettingsPage />);

    expect(await screen.findByText("Product readiness")).toBeInTheDocument();
    expect(screen.getByText("Not production-ready")).toBeInTheDocument();
  });

  it("downloads a local data export from settings", async () => {
    const createObjectURL = vi.fn(() => "blob:careero-export");
    const revokeObjectURL = vi.fn();
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    const append = vi.spyOn(document.body, "append");
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(readiness))
        .mockResolvedValueOnce(
          jsonResponse({
            metadata: {
              schema_version: "careero.local_data_export.v1",
              generated_at: "2026-05-26T12:00:00Z",
              readiness_note: "Local-first JSON export.",
              current_user: {
                id: "00000000-0000-4000-8000-000000000001",
                email: "local-user@careero.local",
                display_name: "Local User",
                mode: "local",
                environment: "local",
              },
              derived_data_notes: [],
            },
            opportunities: [{ id: "role-1" }],
            workspaces: [],
            companies: [],
            job_sources: [],
            resume_sources: [],
            resume_source_versions: [],
            compass_evaluations: [],
            generated_artifacts: [],
            artifact_performance_records: [],
            applications: [],
            application_state_history: [],
            notes: [],
            reminders: [],
            external_links: [],
            interview_stages: [],
            activity_logs: [],
            automation_suggestions: [],
            automation_approval_logs: [],
          }),
        ),
    );

    render(<SettingsPage />);
    await screen.findByText("Local data export");
    await userEvent.click(screen.getByRole("button", { name: /download json/i }));

    expect(await screen.findByText("Export prepared with 1 opportunities.")).toBeInTheDocument();
    expect(createObjectURL).toHaveBeenCalled();
    expect(append).toHaveBeenCalled();
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:careero-export");
  });
});
