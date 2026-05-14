import { z } from "zod";

import {
  EmploymentTypeSchema,
  OpportunitySourceTypeSchema,
  OpportunityStatusSchema,
  RemoteTypeSchema,
} from "./enums.js";
import {
  AuditTimestampsSchema,
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
  MoneySchema,
  TagsSchema,
  UrlSchema,
} from "./primitives.js";

export const OpportunityCompanySchema = z.object({
  name: z.string().min(1),
  websiteUrl: UrlSchema.nullable(),
  industry: z.string().nullable(),
  notes: z.string().nullable(),
});

export const OpportunityLocationSchema = z.object({
  label: z.string().nullable(),
  city: z.string().nullable(),
  region: z.string().nullable(),
  country: z.string().nullable(),
  timezone: z.string().nullable(),
});

export const OpportunityProvenanceSchema = z.object({
  sourceType: OpportunitySourceTypeSchema,
  sourceName: z.string().nullable(),
  sourceUrl: UrlSchema.nullable(),
  externalId: z.string().nullable(),
  ingestionMethod: z.enum(["manual", "ai_parse", "import", "connector"]).default("manual"),
  ingestionTimestamp: IsoDateTimeSchema,
  parserVersion: z.string().nullable(),
  rawContentHash: z.string().nullable(),
  warnings: z.array(z.string()).default([]),
});

export const OpportunityNormalizedContentSchema = z.object({
  title: z.string().min(1),
  companyName: z.string().min(1),
  description: z.string().nullable(),
  responsibilities: z.array(z.string()).default([]),
  requirements: z.array(z.string()).default([]),
  skills: z.array(z.string()).default([]),
  seniority: z.string().nullable(),
  employmentType: EmploymentTypeSchema,
  remoteType: RemoteTypeSchema,
  location: OpportunityLocationSchema,
  compensation: MoneySchema.nullable(),
});

export const OpportunitySchema = ContractEnvelopeSchema.merge(AuditTimestampsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  title: z.string().min(1).max(240),
  company: OpportunityCompanySchema,
  source: OpportunityProvenanceSchema,
  rawSourceContent: z.string().nullable(),
  normalizedContent: OpportunityNormalizedContentSchema,
  compensation: MoneySchema.nullable(),
  location: OpportunityLocationSchema,
  remoteType: RemoteTypeSchema,
  employmentType: EmploymentTypeSchema,
  ingestionTimestamp: IsoDateTimeSchema,
  parseConfidence: z.record(z.number().min(0).max(1)).default({}),
  aiNotes: z.string().nullable(),
  tags: TagsSchema,
  roleStatus: OpportunityStatusSchema,
  linkedEvaluationIds: z.array(IdSchema).default([]),
  linkedApplicationStateId: IdSchema.nullable(),
  linkedArtifactIds: z.array(IdSchema).default([]),
  opportunityMetadata: MetadataSchema,
});

export type OpportunityCompany = z.infer<typeof OpportunityCompanySchema>;
export type OpportunityLocation = z.infer<typeof OpportunityLocationSchema>;
export type OpportunityProvenance = z.infer<typeof OpportunityProvenanceSchema>;
export type OpportunityNormalizedContent = z.infer<typeof OpportunityNormalizedContentSchema>;
export type Opportunity = z.infer<typeof OpportunitySchema>;
