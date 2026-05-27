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
    durable_metering_status: "local_usage_events",
  },
  auth_status: { status: "local_password_enabled", implemented: true, detail: "" },
  tenant_boundary_prep_status: {
    status: "local_boundary_prep",
    implemented: true,
    detail: "",
  },
  billing_status: { status: "not_implemented", implemented: false, detail: "" },
  export_delete_status: {
    status: "local_export_and_request_tracking",
    implemented: true,
    detail: "",
  },
  retention_status: { status: "not_enforced", implemented: false, detail: "" },
  durable_usage_metering_status: {
    status: "local_usage_events",
    implemented: true,
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

const lifecycleList = {
  requests: [],
  lifecycle_note:
    "Local lifecycle requests are audit records only. They do not delete, anonymize, recover, or submit support work.",
};

function fetchByPath(overrides: Record<string, unknown> = {}) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const path = String(input);
    const method = init?.method ?? "GET";
    if (path === "/api/productization/readiness") {
      return Promise.resolve(jsonResponse(readiness));
    }
    if (path === "/api/account/lifecycle-requests" && method === "GET") {
      return Promise.resolve(
        jsonResponse(overrides.lifecycleList ?? lifecycleList),
      );
    }
    if (path === "/api/account/lifecycle-requests" && method === "POST") {
      return Promise.resolve(
        jsonResponse(
          overrides.lifecycleCreate ?? {
            id: "request-1",
            user_id: "00000000-0000-4000-8000-000000000001",
            request_type: "account_deletion",
            status: "requested",
            requested_at: "2026-05-26T12:00:00Z",
            acknowledged_at: null,
            completed_at: null,
            canceled_at: null,
            request_reason: "User recorded a local deletion request from Settings.",
            target_type: null,
            target_id: null,
            request_metadata: {},
            created_at: "2026-05-26T12:00:00Z",
            updated_at: "2026-05-26T12:00:00Z",
            message:
              "Deletion request recorded locally. Data has not been deleted; deletion enforcement remains future.",
          },
        ),
      );
    }
    if (path === "/api/usage/ai?limit=25") {
      return Promise.resolve(
        jsonResponse(
          overrides.aiUsage ?? {
            events: [],
            summary: {
              total_events: 0,
              by_feature: {},
              by_event_type: {},
            },
            usage_note:
              "Local AI usage metering records safe metadata only. It is not billing, credits, paid quota enforcement, or a production cost-control system.",
          },
        ),
      );
    }
    if (path === "/api/entitlements/current") {
      return Promise.resolve(
        jsonResponse(
          overrides.entitlements ?? {
            plan_id: "local_free",
            plan_display_name: "Local Free",
            billing_status: "not_configured",
            payment_provider: "none",
            entitlements: [
              {
                key: "opportunity_capture",
                enabled: true,
                category: "essential_workflow",
                description: "Capture and organize opportunities locally.",
              },
              {
                key: "local_data_export",
                enabled: true,
                category: "data_ownership",
                description: "Export current local-user data as JSON.",
              },
            ],
            feature_limits: [],
            unavailable_future_features: [
              "billing_provider_checkout",
              "employer_sponsored_ranking",
            ],
            monetization_guardrails: ["No payment provider is configured."],
            local_first_note:
              "The local_free plan is a local-first boundary model only.",
            metadata: { schema_version: "careero.local_entitlements.v1" },
          },
        ),
      );
    }
    if (path === "/api/data-export/local") {
      return Promise.resolve(
        jsonResponse(
          overrides.dataExport ?? {
            metadata: {
              schema_version: "careero.local_data_export.v1",
              generated_at: "2026-05-26T12:00:00Z",
              readiness_note: "Local-first JSON export.",
              current_user: {
                id: "00000000-0000-4000-8000-000000000001",
                email: "local-user@careero.local",
                first_name: "Local",
                last_name: "User",
                display_name: "Local User",
                salutation: null,
                pronouns: null,
                headshot_url: null,
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
            account_lifecycle_requests: [],
            ai_usage_events: [],
            automation_suggestions: [],
            automation_approval_logs: [],
          },
        ),
      );
    }
    return Promise.reject(new Error(`Unexpected fetch ${method} ${path}`));
  });
}

describe("SettingsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the product readiness panel", async () => {
    vi.stubGlobal("fetch", fetchByPath());

    render(<SettingsPage />);

    expect(await screen.findByText("Product readiness")).toBeInTheDocument();
    expect(screen.getByText("Not production-ready")).toBeInTheDocument();
    expect(
      screen.queryByText("Authentication and workspace switching are intentionally absent."),
    ).not.toBeInTheDocument();
    expect(screen.getByText("First-party email/password login is enabled locally.")).toBeInTheDocument();
  });

  it("downloads a local data export from settings", async () => {
    const createObjectURL = vi.fn(() => "blob:careero-export");
    const revokeObjectURL = vi.fn();
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    const append = vi.spyOn(document.body, "append");
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    vi.stubGlobal("fetch", fetchByPath());

    render(<SettingsPage />);
    await screen.findByText("Local data export");
    await userEvent.click(screen.getByRole("button", { name: /download json/i }));

    expect(await screen.findByText("Export prepared with 1 opportunities.")).toBeInTheDocument();
    expect(createObjectURL).toHaveBeenCalled();
    expect(append).toHaveBeenCalled();
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:careero-export");
  });

  it("requires confirmation before recording a local deletion request", async () => {
    const fetchMock = fetchByPath();
    vi.stubGlobal("fetch", fetchMock);

    render(<SettingsPage />);
    const deletionButton = await screen.findByRole("button", {
      name: /record deletion request/i,
    });
    expect(deletionButton).toBeDisabled();

    await userEvent.click(
      screen.getByLabelText(
        "I understand this records a request and does not delete data.",
      ),
    );
    expect(deletionButton).not.toBeDisabled();

    await userEvent.click(deletionButton);

    expect(
      await screen.findByText(
        "Deletion request recorded locally. Data has not been deleted; deletion enforcement remains future.",
      ),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/account/lifecycle-requests",
      expect.objectContaining({
        method: "POST",
      }),
    );
  });

  it("shows local AI usage without private content", async () => {
    vi.stubGlobal(
      "fetch",
      fetchByPath({
        aiUsage: {
          events: [
            {
              id: "usage-1",
              user_id: "00000000-0000-4000-8000-000000000001",
              workspace_id: null,
              role_id: null,
              application_id: null,
              artifact_id: null,
              feature: "parse_opportunity",
              event_type: "completed",
              provider: "openai",
              model: "gpt-5-mini",
              status: "completed",
              prompt_version: null,
              ruleset_version: null,
              input_token_estimate: 12,
              output_token_estimate: 8,
              latency_ms: 25,
              error_class: null,
              content_hash: "sha256:safe",
              metadata: {},
              created_at: "2026-05-26T12:00:00Z",
            },
          ],
          summary: {
            total_events: 1,
            by_feature: { parse_opportunity: 1 },
            by_event_type: { completed: 1 },
          },
          usage_note: "Local AI usage metering records safe metadata only.",
        },
      }),
    );

    render(<SettingsPage />);

    expect(await screen.findByText("AI usage")).toBeInTheDocument();
    expect(screen.getByText("parse opportunity")).toBeInTheDocument();
    expect(screen.getByText("openai / gpt-5-mini")).toBeInTheDocument();
    expect(screen.queryByText(/raw resume/i)).not.toBeInTheDocument();
  });

  it("shows the local plan without upgrade or checkout actions", async () => {
    vi.stubGlobal("fetch", fetchByPath());

    render(<SettingsPage />);

    expect(await screen.findByText("Local plan")).toBeInTheDocument();
    expect(screen.getByText("Local Free")).toBeInTheDocument();
    expect(screen.getByText("Billing not configured")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /upgrade/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /checkout/i })).not.toBeInTheDocument();
  });
});
