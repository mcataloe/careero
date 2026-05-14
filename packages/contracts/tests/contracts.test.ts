import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  ApplicationStateSchema,
  CONTRACT_VERSION,
  OpportunitySchema,
  WorkspaceSchema,
  canonicalExamples,
  canonicalSchemaRegistry,
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

  it("requires state history for application state", () => {
    const invalid = { ...canonicalExamples.ApplicationState, stateHistory: [] };

    expect(ApplicationStateSchema.safeParse(invalid).success).toBe(false);
  });
});

describe("generated JSON Schema exports", () => {
  const schemaDir = join(process.cwd(), "generated", "json-schema");
  const expectedFiles = [
    "workspace.schema.json",
    "opportunity.schema.json",
    "stride-evaluation.schema.json",
    "resume-artifact.schema.json",
    "cover-letter-artifact.schema.json",
    "application-state.schema.json",
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
