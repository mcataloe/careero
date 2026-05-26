import { afterEach, describe, expect, it, vi } from "vitest";

import { ProductReadinessPanel } from "./ProductReadinessPanel";
import { render, screen } from "../test-utils";
import type { ProductizationReadiness } from "../types/productization";

function jsonResponse(data: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
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
    core_workflow: {
      status: "local_available",
      implemented: true,
      detail: "Core workflow exists locally.",
    },
    application_workflow: {
      status: "local_available",
      implemented: true,
      detail: "Application workflow exists locally.",
    },
    artifact_lifecycle: {
      status: "incomplete",
      implemented: false,
      detail: "Artifact lifecycle is incomplete.",
    },
    integrations: {
      status: "local_only",
      implemented: false,
      detail: "Integrations are local only.",
    },
    automation: {
      status: "local_guardrails_only",
      implemented: true,
      detail: "External actions are disabled.",
    },
  },
  database_health: "available",
  ai_feature_flags: {
    role_parsing_enabled: true,
    compass_enrichment_enabled: false,
    resume_generation_enabled: true,
    cover_letter_generation_enabled: false,
    provider_key_configured: false,
    local_session_attempt_cap: 25,
    durable_metering_status: "not_implemented",
  },
  auth_status: {
    status: "not_implemented",
    implemented: false,
    detail: "Production auth is not implemented.",
  },
  tenant_boundary_prep_status: {
    status: "local_boundary_prep",
    implemented: true,
    detail: "Boundary prep only.",
  },
  billing_status: {
    status: "not_implemented",
    implemented: false,
    detail: "Billing is not implemented.",
  },
  export_delete_status: {
    status: "local_export_available",
    implemented: true,
    detail: "Local export exists; hosted export and deletion remain future.",
  },
  retention_status: {
    status: "not_enforced",
    implemented: false,
    detail: "Retention is not enforced.",
  },
  durable_usage_metering_status: {
    status: "not_implemented",
    implemented: false,
    detail: "Durable usage metering is not implemented.",
  },
  deployment_status: {
    status: "local_only",
    implemented: true,
    detail: "Cloud deployment remains future.",
  },
  hosted_collaboration_status: {
    status: "not_implemented",
    implemented: false,
    detail: "Hosted collaboration is not implemented.",
  },
  marketplace_employer_side_status: {
    status: "not_implemented",
    implemented: false,
    detail: "Marketplace is not implemented.",
  },
  known_blockers: [
    "Production authentication is not implemented.",
    "Billing, subscriptions, invoices, checkout, and payment flows are not implemented.",
  ],
  production_readiness_statement:
    "Careero is not production-ready unless all required productization gates pass.",
};

describe("ProductReadinessPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders loading state", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));

    render(<ProductReadinessPanel />);

    expect(screen.getByText("Loading product readiness")).toBeInTheDocument();
  });

  it("renders readiness details without claiming production readiness", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(jsonResponse(readiness)));

    render(<ProductReadinessPanel />);

    expect(await screen.findByText("Product readiness")).toBeInTheDocument();
    expect(screen.getByText("Not production-ready")).toBeInTheDocument();
    expect(screen.getByText("local")).toBeInTheDocument();
    expect(screen.getByText("local poc")).toBeInTheDocument();
    expect(screen.getByText("Role parsing: Enabled")).toBeInTheDocument();
    expect(screen.getByText("COMPASS enrichment: Disabled")).toBeInTheDocument();
    expect(screen.queryByText("Production ready")).toBeNull();
  });

  it("renders error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse({ detail: "Backend unavailable" }, 500)),
    );

    render(<ProductReadinessPanel />);

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });
});
