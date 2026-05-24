import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { zodToJsonSchema } from "zod-to-json-schema";

import { CONTRACT_VERSION, canonicalSchemaRegistry } from "../src/index.js";

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const outputDir = join(packageRoot, "generated", "json-schema");

const fileNames: Record<keyof typeof canonicalSchemaRegistry, string> = {
  Workspace: "workspace.schema.json",
  Opportunity: "opportunity.schema.json",
  StrideEvaluation: "stride-evaluation.schema.json",
  ResumeArtifact: "resume-artifact.schema.json",
  CoverLetterArtifact: "cover-letter-artifact.schema.json",
  ApplicationState: "application-state.schema.json",
  AutomationSuggestion: "automation-suggestion.schema.json",
  AutomationApprovalLog: "automation-approval-log.schema.json",
  AutomationPreferences: "automation-preferences.schema.json",
  SearchTrackStrategySummary: "search-track-strategy-summary.schema.json",
  CrossTrackStrategyComparison: "cross-track-strategy-comparison.schema.json",
  CareerStrategySummary: "career-strategy-summary.schema.json",
};

mkdirSync(outputDir, { recursive: true });

for (const [name, schema] of Object.entries(canonicalSchemaRegistry)) {
  const jsonSchema = zodToJsonSchema(schema, {
    name,
    $refStrategy: "root",
    target: "jsonSchema7",
  });

  writeFileSync(
    join(outputDir, fileNames[name as keyof typeof canonicalSchemaRegistry]),
    `${JSON.stringify(jsonSchema, null, 2)}\n`,
  );
}

writeFileSync(
  join(outputDir, "index.json"),
  `${JSON.stringify(
    {
      contractVersion: CONTRACT_VERSION,
      schemas: fileNames,
    },
    null,
    2,
  )}\n`,
);
