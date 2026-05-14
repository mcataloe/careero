import { z } from "zod";

import {
  CoverLetterToneSchema,
  ExportFormatSchema,
  ResumeArtifactTypeSchema,
} from "./enums.js";
import {
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
  ModelMetadataSchema,
  TimestampFieldsSchema,
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

export const FormatMetadataSchema = z.object({
  primaryFormat: ExportFormatSchema,
  availableFormats: z.array(ExportFormatSchema).default([]),
  contentHash: z.string().nullable(),
});

export const ResumeArtifactSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  opportunityId: IdSchema.nullable(),
  sourceArtifactId: IdSchema.nullable(),
  artifactType: ResumeArtifactTypeSchema,
  title: z.string().min(1),
  content: z.string().min(1),
  formatMetadata: FormatMetadataSchema,
  generationMetadata: ArtifactGenerationMetadataSchema,
  exportMetadata: z.array(ArtifactExportSchema).default([]),
  revision: ArtifactRevisionSchema,
  uploadMetadata: ArtifactUploadMetadataSchema.nullable(),
  parsingMetadata: ArtifactParsingMetadataSchema.nullable(),
  tailoringNotes: z.string().nullable(),
  metadata: MetadataSchema,
});

export const CoverLetterEditHistoryEntrySchema = z.object({
  editedAt: IsoDateTimeSchema,
  editedBy: z.enum(["user", "ai", "system"]).default("user"),
  summary: z.string().nullable(),
});

export const CoverLetterArtifactSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  opportunityId: IdSchema.nullable(),
  title: z.string().min(1),
  content: z.string().min(1),
  tone: CoverLetterToneSchema,
  generationMetadata: ArtifactGenerationMetadataSchema,
  editHistory: z.array(CoverLetterEditHistoryEntrySchema).default([]),
  exportMetadata: z.array(ArtifactExportSchema).default([]),
  revision: ArtifactRevisionSchema,
  metadata: MetadataSchema,
});

export type ResumeArtifact = z.infer<typeof ResumeArtifactSchema>;
export type CoverLetterArtifact = z.infer<typeof CoverLetterArtifactSchema>;
