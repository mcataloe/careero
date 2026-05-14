import { z } from "zod";

import {
  ConfidenceLevelSchema,
  EvaluationStatusSchema,
  RecommendationSchema,
} from "./enums.js";
import {
  ContractEnvelopeSchema,
  IdSchema,
  MetadataSchema,
  ModelMetadataSchema,
  ScoredTextSchema,
  TimestampFieldsSchema,
  VersionMetadataSchema,
} from "./primitives.js";

export const EvaluationSectionSchema = z.object({
  status: z.enum(["strong_match", "partial_match", "no_evidence", "insufficient_data", "risk"]),
  score: z.number().min(0).max(100).nullable(),
  summary: z.string().nullable(),
  evidence: z.array(z.string()).default([]),
  gaps: z.array(z.string()).default([]),
  assumptions: z.array(z.string()).default([]),
});

export const AtsFindingsSchema = z.object({
  matchedKeywords: z.array(z.string()).default([]),
  missingKeywords: z.array(z.string()).default([]),
  keywordNotes: z.string().nullable(),
  score: z.number().min(0).max(100).nullable(),
});

export const CompensationFindingsSchema = z.object({
  status: z.enum(["aligned", "below_target", "above_target", "unknown", "needs_review"]),
  notes: z.string().nullable(),
  evidence: z.array(z.string()).default([]),
  score: z.number().min(0).max(100).nullable(),
});

export const EvaluationRecommendationsSchema = z.object({
  decision: RecommendationSchema,
  rationale: z.string().min(1),
  nextActions: z.array(z.string()).default([]),
});

export const EvaluationConfidenceSchema = z.object({
  level: ConfidenceLevelSchema,
  score: z.number().min(0).max(1).nullable(),
  rationale: z.string().nullable(),
});

export const EvaluationReproducibilitySchema = z.object({
  inputHash: z.string().min(1),
  roleContentHash: z.string().nullable(),
  sourceHash: z.string().nullable(),
  promptVersion: z.string().min(1),
  rulesetVersion: z.string().min(1),
  sourceHashes: z.record(z.string()).default({}),
  deterministicBaseline: z.record(z.unknown()).nullable(),
});

export const StrideEvaluationSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  opportunityId: IdSchema,
  version: VersionMetadataSchema,
  status: EvaluationStatusSchema,
  modelMetadata: ModelMetadataSchema,
  summary: z.string().nullable(),
  overallScore: z.number().min(0).max(100).nullable(),
  strengths: z.array(ScoredTextSchema).default([]),
  gaps: z.array(ScoredTextSchema).default([]),
  risks: z.array(ScoredTextSchema).default([]),
  atsFindings: AtsFindingsSchema,
  compensationFindings: CompensationFindingsSchema,
  recommendations: EvaluationRecommendationsSchema.nullable(),
  confidence: EvaluationConfidenceSchema,
  sections: z.object({
    strategicFit: EvaluationSectionSchema,
    technicalAlignment: EvaluationSectionSchema,
    seniorityAlignment: EvaluationSectionSchema,
    compensationAlignment: EvaluationSectionSchema,
    remoteAlignment: EvaluationSectionSchema,
    companyRisk: EvaluationSectionSchema,
    applicationEffort: EvaluationSectionSchema,
    atsResumeAlignment: EvaluationSectionSchema,
  }),
  assumptions: z.array(z.string()).default([]),
  reproducibility: EvaluationReproducibilitySchema,
  metadata: MetadataSchema,
});

export type EvaluationSection = z.infer<typeof EvaluationSectionSchema>;
export type StrideEvaluation = z.infer<typeof StrideEvaluationSchema>;
