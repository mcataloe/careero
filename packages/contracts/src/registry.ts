import { z } from "zod";

import { ApplicationStateSchema } from "./application-state.js";
import { CoverLetterArtifactSchema, ResumeArtifactSchema } from "./artifacts.js";
import {
  AutomationApprovalLogSchema,
  AutomationPreferencesSchema,
  AutomationSuggestionSchema,
} from "./automation.js";
import { OpportunitySchema } from "./opportunity.js";
import { StrideEvaluationSchema } from "./stride-evaluation.js";
import { WorkspaceSchema } from "./workspace.js";

export const canonicalSchemaRegistry = {
  Workspace: WorkspaceSchema,
  Opportunity: OpportunitySchema,
  StrideEvaluation: StrideEvaluationSchema,
  ResumeArtifact: ResumeArtifactSchema,
  CoverLetterArtifact: CoverLetterArtifactSchema,
  ApplicationState: ApplicationStateSchema,
  AutomationSuggestion: AutomationSuggestionSchema,
  AutomationApprovalLog: AutomationApprovalLogSchema,
  AutomationPreferences: AutomationPreferencesSchema,
} as const satisfies Record<string, z.ZodTypeAny>;

export type CanonicalSchemaName = keyof typeof canonicalSchemaRegistry;
