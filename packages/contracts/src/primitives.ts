import { z } from "zod";

export const CONTRACT_VERSION = "careero.contracts.v1" as const;

export const IdSchema = z.string().uuid();
export const IsoDateTimeSchema = z.string().datetime({ offset: true });
export const IsoDateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
export const UrlSchema = z.string().url();

export const MetadataSchema = z.record(z.unknown());
export const TagsSchema = z.array(z.string().min(1).max(80)).default([]);

export const MoneySchema = z.object({
  min: z.number().nonnegative().nullable(),
  max: z.number().nonnegative().nullable(),
  currency: z.string().length(3).nullable(),
  period: z.enum(["hourly", "daily", "weekly", "monthly", "annual", "project"]).nullable(),
  sourceText: z.string().nullable(),
}).superRefine((money, context) => {
  if (money.min !== null && money.max !== null && money.min > money.max) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["max"],
      message: "max must be greater than or equal to min",
    });
  }
});

export const AuditTimestampsSchema = z.object({
  createdAt: IsoDateTimeSchema,
  updatedAt: IsoDateTimeSchema,
  archivedAt: IsoDateTimeSchema.nullable(),
  deletedAt: IsoDateTimeSchema.nullable(),
});

export const ModelMetadataSchema = z.object({
  provider: z.string().min(1),
  model: z.string().min(1),
  promptVersion: z.string().min(1).nullable(),
  rulesetVersion: z.string().min(1).nullable(),
  inputTokenEstimate: z.number().int().nonnegative().nullable(),
  outputTokenEstimate: z.number().int().nonnegative().nullable(),
  latencyMs: z.number().int().nonnegative().nullable(),
});

export const ProvenanceSchema = z.object({
  sourceType: z.string().min(1),
  sourceName: z.string().nullable(),
  sourceUrl: UrlSchema.nullable(),
  importedAt: IsoDateTimeSchema,
  parserVersion: z.string().nullable(),
  rawContentHash: z.string().nullable(),
  warnings: z.array(z.string()).default([]),
});

export const ContractEnvelopeSchema = z.object({
  contractVersion: z.literal(CONTRACT_VERSION),
});

export const LinkSchema = z.object({
  label: z.string().min(1),
  url: UrlSchema,
  type: z.string().min(1).nullable(),
});

export const ScoredTextSchema = z.object({
  label: z.string().min(1),
  score: z.number().min(0).max(1).nullable(),
  evidence: z.array(z.string()).default([]),
  notes: z.string().nullable(),
});

export const VersionMetadataSchema = z.object({
  version: z.string().min(1),
  previousVersion: z.string().min(1).nullable(),
  changeReason: z.string().nullable(),
});

export type Money = z.infer<typeof MoneySchema>;
export type ModelMetadata = z.infer<typeof ModelMetadataSchema>;
export type Provenance = z.infer<typeof ProvenanceSchema>;
export type Link = z.infer<typeof LinkSchema>;
