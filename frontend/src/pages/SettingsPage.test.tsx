import { afterEach, describe, expect, it, vi } from "vitest";

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
  auth_status: { status: "local_password_enabled", implemented: true, detail: "" },
  tenant_boundary_prep_status: {
    status: "local_boundary_prep",
    implemented: true,
    detail: "",
  },
  billing_status: { status: "not_implemented", implemented: false, detail: "" },
  export_delete_status: { status: "not_implemented", implemented: false, detail: "" },
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
  known_blockers: ["Production auth hardening is incomplete."],
  production_readiness_statement:
    "Careero is not production-ready unless all required productization gates pass.",
};

describe("SettingsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the product readiness panel", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse(readiness)));

    render(<SettingsPage />);

    expect(await screen.findByText("Product readiness")).toBeInTheDocument();
    expect(screen.getByText("Not production-ready")).toBeInTheDocument();
    expect(
      screen.queryByText("Authentication and workspace switching are intentionally absent."),
    ).not.toBeInTheDocument();
    expect(screen.getByText("First-party username/password login is enabled locally.")).toBeInTheDocument();
  });
});
