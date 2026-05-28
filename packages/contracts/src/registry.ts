import { z } from "zod";

import { ApplicationStateSchema } from "./application-state.js";
import { CoverLetterArtifactSchema, ResumeArtifactSchema } from "./artifacts.js";
import {
  AutomationApprovalLogSchema,
  AutomationPreferencesSchema,
  AutomationSuggestionSchema,
} from "./automation.js";
import { OpportunitySchema } from "./opportunity.js";
import {
  CareerStrategySummarySchema,
  CrossTrackStrategyComparisonSchema,
  SearchTrackStrategySummarySchema,
} from "./strategy.js";
import { CompassEvaluationSchema } from "./compass-evaluation.js";
import { InsightSchema } from "./insights.js";
import { WorkspaceSchema } from "./workspace.js";

export const canonicalSchemaRegistry = {
  Workspace: WorkspaceSchema,
  Opportunity: OpportunitySchema,
  CompassEvaluation: CompassEvaluationSchema,
  Insight: InsightSchema,
  ResumeArtifact: ResumeArtifactSchema,
  CoverLetterArtifact: CoverLetterArtifactSchema,
  ApplicationState: ApplicationStateSchema,
  AutomationSuggestion: AutomationSuggestionSchema,
  AutomationApprovalLog: AutomationApprovalLogSchema,
  AutomationPreferences: AutomationPreferencesSchema,
  SearchTrackStrategySummary: SearchTrackStrategySummarySchema,
  CrossTrackStrategyComparison: CrossTrackStrategyComparisonSchema,
  CareerStrategySummary: CareerStrategySummarySchema,
} as const satisfies Record<string, z.ZodTypeAny>;

export type CanonicalSchemaName = keyof typeof canonicalSchemaRegistry;
