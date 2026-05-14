import { z } from "zod";

import {
  EmploymentTypeSchema,
  OpportunitySourceTypeSchema,
  OpportunityStatusSchema,
  RemoteTypeSchema,
} from "./enums.js";
import {
  ContractEnvelopeSchema,
  IdSchema,
  MetadataSchema,
  MoneySchema,
  TagsSchema,
  TimestampFieldsSchema,
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

export const OpportunityNormalizedContentSchema = z.object({
  description: z.string().nullable(),
  responsibilities: z.array(z.string()).default([]),
  requirements: z.array(z.string()).default([]),
  skills: z.array(z.string()).default([]),
  seniority: z.string().nullable(),
  notes: z.string().nullable(),
});

export const OpportunitySchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  sourceType: OpportunitySourceTypeSchema,
  sourceUrl: UrlSchema.nullable(),
  rawContent: z.string().nullable(),
  normalizedContent: OpportunityNormalizedContentSchema,
  company: OpportunityCompanySchema,
  title: z.string().min(1).max(240),
  employmentType: EmploymentTypeSchema,
  compensation: MoneySchema.nullable(),
  location: OpportunityLocationSchema,
  remoteMode: RemoteTypeSchema,
  parseConfidence: z.record(z.number().min(0).max(1)).default({}),
  tags: TagsSchema,
  status: OpportunityStatusSchema,
  metadata: MetadataSchema,
});

export type OpportunityCompany = z.infer<typeof OpportunityCompanySchema>;
export type OpportunityLocation = z.infer<typeof OpportunityLocationSchema>;
export type OpportunityNormalizedContent = z.infer<typeof OpportunityNormalizedContentSchema>;
export type Opportunity = z.infer<typeof OpportunitySchema>;
