import { z } from "zod";

import {
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
} from "./primitives.js";

export const StrategyInsufficientDataReasonSchema = z.enum([
  "empty_workspace",
  "few_opportunities",
  "few_applications",
  "few_outcomes",
  "missing_stride_evaluations",
  "missing_compensation_ranges",
  "missing_artifact_performance",
  "missing_source_history",
  "stale_track",
  "unknown",
]);

export const StrategyConfidenceSchema = z.object({
  confidence: z.enum(["insufficient_data", "weak", "moderate", "high"]),
  basis: z.string().min(1),
  sampleSize: z.number().int().nonnegative(),
  sourceInputs: MetadataSchema,
  knownUncertainty: z.array(z.string()).default([]),
  insufficientData: z.array(StrategyInsufficientDataReasonSchema).default([]),
  userOverrides: MetadataSchema.nullable().default(null),
});

export const StrategySignalSchema = z.object({
  id: z.string().min(1),
  category: z.enum([
    "search_health",
    "stride",
    "compensation",
    "source",
    "artifact",
    "historical",
    "workspace",
  ]),
  label: z.string().min(1),
  message: z.string().min(1),
  basis: z.string().min(1),
  severity: z.enum(["info", "caution", "positive"]).default("info"),
  confidence: StrategyConfidenceSchema,
  sourceInputs: MetadataSchema,
});

export const StrategyActionCandidateSchema = z.object({
  id: z.string().min(1),
  category: z.enum([
    "review_workspace_targets",
    "review_compensation_target",
    "review_skill_gap_plan",
    "review_artifact_strategy",
    "review_source_strategy",
    "archive_or_pause_track_review",
    "create_followup_plan_preview",
    "review_search_focus",
  ]),
  title: z.string().min(1),
  rationale: z.string().min(1),
  basis: z.string().min(1),
  confidence: StrategyConfidenceSchema,
  sourceInputs: MetadataSchema,
  advisoryOnly: z.literal(true),
});

export const StrategyInsufficientDataItemSchema = z.object({
  reason: StrategyInsufficientDataReasonSchema,
  message: z.string().min(1),
  sourceInputs: MetadataSchema.default({}),
});

export const SearchTrackStrategySummarySchema = ContractEnvelopeSchema.extend({
  workspaceId: IdSchema,
  workspaceName: z.string().min(1),
  generatedAt: IsoDateTimeSchema,
  summary: z.string().min(1),
  basis: z.string().min(1),
  confidence: StrategyConfidenceSchema,
  sampleSize: z.object({
    opportunities: z.number().int().nonnegative(),
    applications: z.number().int().nonnegative(),
    submittedApplications: z.number().int().nonnegative(),
    responses: z.number().int().nonnegative(),
    strideEvaluations: z.number().int().nonnegative(),
    artifactPerformanceRecords: z.number().int().nonnegative(),
  }),
  sourceInputs: MetadataSchema,
  knownUncertainty: z.array(z.string()).default([]),
  insufficientData: z.array(StrategyInsufficientDataItemSchema).default([]),
  signals: z.array(StrategySignalSchema).default([]),
  compensationAlignment: z.object({
    summary: z.string().min(1),
    basis: z.string().min(1),
    confidence: StrategyConfidenceSchema,
    observations: z.array(MetadataSchema).default([]),
  }),
  skillGapThemes: z.array(StrategySignalSchema).default([]),
  roleMarketPositioning: z.object({
    summary: z.string().min(1),
    basis: z.string().min(1),
    confidence: StrategyConfidenceSchema,
    themes: z.array(z.string()).default([]),
  }),
  careerNarrativeThemes: z.array(StrategySignalSchema).default([]),
  retrospective: z.object({
    summary: z.string().min(1),
    basis: z.string().min(1),
    confidence: StrategyConfidenceSchema,
    notes: z.array(z.string()).default([]),
  }),
  actionCandidates: z.array(StrategyActionCandidateSchema).default([]),
  warnings: z.array(z.string()).default([]),
});

export const CrossTrackStrategyComparisonSchema = z.object({
  generatedAt: IsoDateTimeSchema,
  basis: z.string().min(1),
  confidence: StrategyConfidenceSchema,
  tracks: z.array(
    z.object({
      workspaceId: IdSchema,
      workspaceName: z.string().min(1),
      summary: z.string().min(1),
      sampleSize: MetadataSchema,
      signalCount: z.number().int().nonnegative(),
      warningCount: z.number().int().nonnegative(),
    }),
  ),
  signals: z.array(StrategySignalSchema).default([]),
  insufficientData: z.array(StrategyInsufficientDataItemSchema).default([]),
  warnings: z.array(z.string()).default([]),
});

export const CareerStrategySummarySchema = ContractEnvelopeSchema.extend({
  generatedAt: IsoDateTimeSchema,
  summary: z.string().min(1),
  workspaceId: IdSchema.nullable(),
  workspaceName: z.string().nullable(),
  activeTrack: SearchTrackStrategySummarySchema.nullable(),
  tracks: z.array(SearchTrackStrategySummarySchema).default([]),
  crossTrackComparison: CrossTrackStrategyComparisonSchema.nullable(),
  warnings: z.array(z.string()).default([]),
});

export type StrategyInsufficientDataReason = z.infer<
  typeof StrategyInsufficientDataReasonSchema
>;
export type StrategyConfidence = z.infer<typeof StrategyConfidenceSchema>;
export type StrategySignal = z.infer<typeof StrategySignalSchema>;
export type StrategyActionCandidate = z.infer<
  typeof StrategyActionCandidateSchema
>;
export type SearchTrackStrategySummary = z.infer<
  typeof SearchTrackStrategySummarySchema
>;
export type CrossTrackStrategyComparison = z.infer<
  typeof CrossTrackStrategyComparisonSchema
>;
export type CareerStrategySummary = z.infer<typeof CareerStrategySummarySchema>;
