import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  ApplicationStateSchema,
  AutomationApprovalLogSchema,
  AutomationPreferencesSchema,
  AutomationSuggestionSchema,
  CONTRACT_VERSION,
  MoneySchema,
  OpportunitySchema,
  CompassEvaluationSchema,
  WorkspaceSchema,
  canonicalExamples,
  canonicalSchemaRegistry,
  parseWorkspace,
  validateWorkspace,
} from "../src/index.js";

describe("canonical contract examples", () => {
  it("parses every canonical example fixture", () => {
    for (const [name, schema] of Object.entries(canonicalSchemaRegistry)) {
      expect(() => schema.parse(canonicalExamples[name as keyof typeof canonicalExamples])).not.toThrow();
    }
  });

  it("preserves contract shape through serialization", () => {
    for (const [name, schema] of Object.entries(canonicalSchemaRegistry)) {
      const parsed = schema.parse(canonicalExamples[name as keyof typeof canonicalExamples]);
      const roundTripped = JSON.parse(JSON.stringify(parsed));

      expect(schema.parse(roundTripped)).toEqual(parsed);
    }
  });
});

describe("canonical contract validation", () => {
  it("exports the canonical contract version", () => {
    expect(CONTRACT_VERSION).toBe("careero.contracts.v1");
  });

  it("rejects invalid workspace status values", () => {
    const invalid = { ...canonicalExamples.Workspace, status: "running" };

    expect(WorkspaceSchema.safeParse(invalid).success).toBe(false);
  });

  it("requires workspace linkage on opportunities", () => {
    const invalid = { ...canonicalExamples.Opportunity };
    delete (invalid as Partial<typeof invalid>).workspaceId;

    expect(OpportunitySchema.safeParse(invalid).success).toBe(false);
  });

  it("requires version fields for COMPASS evaluations", () => {
    const invalid = { ...canonicalExamples.CompassEvaluation };
    delete (invalid as Partial<typeof invalid>).version;

    expect(CompassEvaluationSchema.safeParse(invalid).success).toBe(false);
  });

  it("requires state history for application state", () => {
    const invalid = { ...canonicalExamples.ApplicationState, stateHistory: [] };

    expect(ApplicationStateSchema.safeParse(invalid).success).toBe(false);
  });

  it("supports structured interview stages for application state", () => {
    const parsed = ApplicationStateSchema.parse(canonicalExamples.ApplicationState);

    expect(parsed.interviewStages[0].stageType).toBe("recruiter_screen");
  });

  it("rejects invalid timestamp formats", () => {
    const invalid = { ...canonicalExamples.Workspace, createdAt: "May 13, 2026" };

    expect(WorkspaceSchema.safeParse(invalid).success).toBe(false);
  });

  it("rejects compensation ranges where min is greater than max", () => {
    const result = MoneySchema.safeParse({
      min: 240000,
      max: 180000,
      currency: "USD",
      period: "annual",
      sourceText: "$240k-$180k",
    });

    expect(result.success).toBe(false);
  });

  it("requires workspace scope for automation suggestions", () => {
    const invalid = { ...canonicalExamples.AutomationSuggestion };
    delete (invalid as Partial<typeof invalid>).workspaceId;

    expect(AutomationSuggestionSchema.safeParse(invalid).success).toBe(false);
  });

  it("rejects automation approval logs that allow external mutation", () => {
    const invalid = {
      ...canonicalExamples.AutomationApprovalLog,
      externalMutation: true,
      preview: {
        ...canonicalExamples.AutomationApprovalLog.preview,
        externalMutation: true,
      },
    };

    expect(AutomationApprovalLogSchema.safeParse(invalid).success).toBe(false);
  });

  it("keeps future external automation disabled in preferences", () => {
    const invalid = {
      ...canonicalExamples.AutomationPreferences,
      futureExternalActionsEnabled: true,
    };

    expect(AutomationPreferencesSchema.safeParse(invalid).success).toBe(false);
  });
});

describe("contract validation helpers", () => {
  it("returns parsed data for valid objects", () => {
    const result = validateWorkspace(canonicalExamples.Workspace);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.id).toBe(canonicalExamples.Workspace.id);
    }
  });

  it("returns validation issues for invalid objects", () => {
    const result = validateWorkspace({ ...canonicalExamples.Workspace, status: "running" });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.issues.length).toBeGreaterThan(0);
    }
  });

  it("throws through entity parse helpers for invalid objects", () => {
    expect(() => parseWorkspace({ ...canonicalExamples.Workspace, status: "running" })).toThrow();
  });
});

describe("generated JSON Schema exports", () => {
  const schemaDir = join(process.cwd(), "generated", "json-schema");
  const expectedFiles = [
    "workspace.schema.json",
    "opportunity.schema.json",
    "compass-evaluation.schema.json",
    "resume-artifact.schema.json",
    "cover-letter-artifact.schema.json",
    "application-state.schema.json",
    "automation-suggestion.schema.json",
    "automation-approval-log.schema.json",
    "automation-preferences.schema.json",
    "search-track-strategy-summary.schema.json",
    "cross-track-strategy-comparison.schema.json",
    "career-strategy-summary.schema.json",
    "index.json",
  ];

  it("writes a JSON Schema file for every canonical entity", () => {
    for (const fileName of expectedFiles) {
      expect(existsSync(join(schemaDir, fileName))).toBe(true);
    }
  });

  it("keeps schema registry names aligned with JSON Schema index", () => {
    const index = JSON.parse(readFileSync(join(schemaDir, "index.json"), "utf8"));

    expect(index.contractVersion).toBe(CONTRACT_VERSION);
    expect(Object.keys(index.schemas).sort()).toEqual(Object.keys(canonicalSchemaRegistry).sort());
  });
});
