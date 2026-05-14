import { z } from "zod";

import { WorkspaceSearchCategorySchema, WorkspaceStatusSchema } from "./enums.js";
import {
  ArchivableTimestampFieldsSchema,
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

export const WorkspaceSchema = ContractEnvelopeSchema.merge(ArchivableTimestampFieldsSchema).extend({
  id: IdSchema,
  userId: IdSchema,
  title: z.string().min(1).max(160),
  description: z.string().nullable(),
  workspaceType: WorkspaceSearchCategorySchema,
  status: WorkspaceStatusSchema,
  preferences: WorkspacePreferencesSchema,
  aiContextSummary: z.string().nullable(),
  tags: TagsSchema,
  metadata: MetadataSchema,
});

export type WorkspacePreferences = z.infer<typeof WorkspacePreferencesSchema>;
export type Workspace = z.infer<typeof WorkspaceSchema>;
