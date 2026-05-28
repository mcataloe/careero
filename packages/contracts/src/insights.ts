import { z } from "zod";

import {
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
  TimestampFieldsSchema,
} from "./primitives.js";

export const InsightCategorySchema = z.enum([
  "fit_alignment",
  "risk_red_flag",
  "compensation",
  "remote_location_alignment",
  "seniority_alignment",
  "application_workflow",
  "artifact_readiness",
  "follow_up_action",
  "cross_opportunity_comparison",
  "search_track_strategy",
  "compass",
  "source_intelligence",
  "historical_learning",
  "other",
  "unknown",
]);

export const InsightGenerationMethodSchema = z.enum([
  "ai_generated",
  "deterministic",
  "user_authored",
  "imported",
  "hybrid",
  "unknown",
]);

export const InsightConfidenceLevelSchema = z.enum([
  "insufficient_data",
  "weak",
  "moderate",
  "high",
  "unknown",
]);

export const InsightSeveritySchema = z.enum([
  "info",
  "positive",
  "caution",
  "warning",
  "critical",
]);

export const InsightVisibilitySchema = z.enum([
  "internal",
  "advisor_visible",
  "user_exportable",
]);

export const InsightSourceReferenceTypeSchema = z.enum([
  "opportunity",
  "raw_job_description",
  "parsed_fields",
  "compass_evaluation",
  "resume_source",
  "artifact",
  "user_note",
  "application_event",
  "workspace",
  "other",
]);

export const InsightScopeSchema = z.object({
  userScoped: z.literal(true).default(true),
  workspaceId: IdSchema.nullable().default(null),
  opportunityId: IdSchema.nullable().default(null),
  compassEvaluationId: IdSchema.nullable().default(null),
  artifactId: IdSchema.nullable().default(null),
  applicationId: IdSchema.nullable().default(null),
});

export const InsightSourceReferenceSchema = z.object({
  sourceType: InsightSourceReferenceTypeSchema,
  sourceId: IdSchema.nullable().default(null),
  label: z.string().min(1),
  field: z.string().min(1).nullable().default(null),
  metadata: MetadataSchema.default({}),
});

export const InsightFreshnessSchema = z.object({
  generatedAt: IsoDateTimeSchema,
  sourceUpdatedAt: IsoDateTimeSchema.nullable().default(null),
  isStale: z.boolean().default(false),
  refreshReason: z.string().min(1).nullable().default(null),
});

export const InsightRecommendedActionSchema = z.object({
  actionType: z.string().min(1),
  label: z.string().min(1),
  routePath: z.string().min(1).nullable().default(null),
  reviewRequired: z.boolean().default(false),
  metadata: MetadataSchema.default({}),
});

export const InsightSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: z.string().min(1),
  category: InsightCategorySchema,
  label: z.string().min(1),
  message: z.string().min(1),
  basis: z.string().min(1),
  confidence: z.string().min(1),
  confidenceLevel: InsightConfidenceLevelSchema,
  confidenceExplanation: z.string().min(1).nullable().default(null),
  knownUncertainty: z.array(z.string().min(1)).default([]),
  warnings: z.array(z.string().min(1)).default([]),
  severity: InsightSeveritySchema.default("info"),
  priority: z.number().int().min(0).max(100).nullable().default(null),
  generationMethod: InsightGenerationMethodSchema.default("deterministic"),
  visibility: InsightVisibilitySchema.default("internal"),
  scope: InsightScopeSchema,
  sourceReferences: z.array(InsightSourceReferenceSchema).default([]),
  sourceInputs: MetadataSchema.default({}),
  freshness: InsightFreshnessSchema,
  recommendedAction: InsightRecommendedActionSchema.nullable().default(null),
  metadata: MetadataSchema.default({}),
});

export type InsightCategory = z.infer<typeof InsightCategorySchema>;
export type InsightGenerationMethod = z.infer<typeof InsightGenerationMethodSchema>;
export type InsightConfidenceLevel = z.infer<typeof InsightConfidenceLevelSchema>;
export type InsightSeverity = z.infer<typeof InsightSeveritySchema>;
export type InsightVisibility = z.infer<typeof InsightVisibilitySchema>;
export type InsightSourceReference = z.infer<typeof InsightSourceReferenceSchema>;
export type InsightFreshness = z.infer<typeof InsightFreshnessSchema>;
export type InsightRecommendedAction = z.infer<typeof InsightRecommendedActionSchema>;
export type Insight = z.infer<typeof InsightSchema>;
