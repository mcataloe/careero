import { z } from "zod";

import { WorkspaceSearchCategorySchema, WorkspaceStatusSchema } from "./enums.js";
import {
  AuditTimestampsSchema,
  ContractEnvelopeSchema,
  IdSchema,
  MetadataSchema,
  MoneySchema,
  TagsSchema,
} from "./primitives.js";

export const WorkspacePreferencesSchema = z.object({
  targetTitles: z.array(z.string().min(1)).default([]),
  targetSeniority: z.array(z.string().min(1)).default([]),
  preferredRemoteTypes: z.array(z.enum(["remote", "hybrid", "onsite"])).default([]),
  preferredLocations: z.array(z.string().min(1)).default([]),
  targetCompensation: MoneySchema.nullable(),
  targetKeywords: z.array(z.string().min(1)).default([]),
  avoidKeywords: z.array(z.string().min(1)).default([]),
  notes: z.string().nullable(),
});

export const WorkspaceSchema = ContractEnvelopeSchema.merge(AuditTimestampsSchema).extend({
  id: IdSchema,
  ownerUserId: IdSchema,
  title: z.string().min(1).max(160),
  description: z.string().nullable(),
  searchCategory: WorkspaceSearchCategorySchema,
  status: WorkspaceStatusSchema,
  preferences: WorkspacePreferencesSchema,
  workspaceMetadata: MetadataSchema,
  aiContextSummary: z.string().nullable(),
  tags: TagsSchema,
});

export type WorkspacePreferences = z.infer<typeof WorkspacePreferencesSchema>;
export type Workspace = z.infer<typeof WorkspaceSchema>;
