import { z } from "zod";

import {
  ArtifactLifecycleStatusSchema,
  ArtifactSourceTypeSchema,
  CoverLetterToneSchema,
  ExportFormatSchema,
  ResumeArtifactTypeSchema,
} from "./enums.js";
import {
  AuditTimestampsSchema,
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
  ModelMetadataSchema,
} from "./primitives.js";

export const ArtifactGenerationMetadataSchema = z.object({
  generatedBy: z.enum(["user", "deterministic_rules", "ai", "import"]).default("user"),
  modelMetadata: ModelMetadataSchema.nullable(),
  promptVersion: z.string().nullable(),
  inputHash: z.string().nullable(),
  groundingSourceIds: z.array(IdSchema).default([]),
  warnings: z.array(z.string()).default([]),
});

export const ArtifactExportSchema = z.object({
  format: ExportFormatSchema,
  exportedAt: IsoDateTimeSchema.nullable(),
  fileName: z.string().nullable(),
  contentHash: z.string().nullable(),
});

export const ArtifactRevisionSchema = z.object({
  revisionId: IdSchema,
  parentArtifactId: IdSchema.nullable(),
  revisionNumber: z.number().int().positive(),
  changeSummary: z.string().nullable(),
  createdAt: IsoDateTimeSchema,
});

export const ArtifactUploadMetadataSchema = z.object({
  originalFileName: z.string().nullable(),
  contentType: z.string().nullable(),
  sizeBytes: z.number().int().nonnegative().nullable(),
  uploadedAt: IsoDateTimeSchema.nullable(),
  contentHash: z.string().nullable(),
});

export const ArtifactParsingMetadataSchema = z.object({
  parserVersion: z.string().nullable(),
  parsedAt: IsoDateTimeSchema.nullable(),
  warnings: z.array(z.string()).default([]),
});

export const ResumeArtifactSchema = ContractEnvelopeSchema.merge(AuditTimestampsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  sourceResumeId: IdSchema.nullable(),
  targetOpportunityId: IdSchema.nullable(),
  artifactType: ResumeArtifactTypeSchema,
  sourceType: ArtifactSourceTypeSchema,
  title: z.string().min(1),
  content: z.string().min(1),
  generationMetadata: ArtifactGenerationMetadataSchema,
  exportFormats: z.array(ArtifactExportSchema).default([]),
  revision: ArtifactRevisionSchema,
  uploadMetadata: ArtifactUploadMetadataSchema.nullable(),
  parsingMetadata: ArtifactParsingMetadataSchema.nullable(),
  tailoringNotes: z.string().nullable(),
  status: ArtifactLifecycleStatusSchema,
  exportedAt: IsoDateTimeSchema.nullable(),
  artifactMetadata: MetadataSchema,
});

export const CoverLetterEditHistoryEntrySchema = z.object({
  editedAt: IsoDateTimeSchema,
  editedBy: z.enum(["user", "ai", "system"]).default("user"),
  summary: z.string().nullable(),
});

export const CoverLetterArtifactSchema = ContractEnvelopeSchema.merge(AuditTimestampsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  targetOpportunityId: IdSchema,
  title: z.string().min(1),
  content: z.string().min(1),
  tone: CoverLetterToneSchema,
  generationMetadata: ArtifactGenerationMetadataSchema,
  editHistory: z.array(CoverLetterEditHistoryEntrySchema).default([]),
  exportFormats: z.array(ArtifactExportSchema).default([]),
  revision: ArtifactRevisionSchema,
  status: ArtifactLifecycleStatusSchema,
  exportedAt: IsoDateTimeSchema.nullable(),
  artifactMetadata: MetadataSchema,
});

export type ResumeArtifact = z.infer<typeof ResumeArtifactSchema>;
export type CoverLetterArtifact = z.infer<typeof CoverLetterArtifactSchema>;
