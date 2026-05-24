import { z } from "zod";

import {
  AutomationActionTypeSchema,
  AutomationApprovalStatusSchema,
  AutomationExecutionStatusSchema,
  AutomationSuggestionStatusSchema,
  AutomationTargetTypeSchema,
} from "./enums.js";
import {
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  MetadataSchema,
  TimestampFieldsSchema,
} from "./primitives.js";

export const AutomationPreviewSchema = z.object({
  title: z.string().min(1),
  body: z.string().min(1),
  contentHash: z.string().min(1),
  externalMutation: z.literal(false),
});

export const AutomationSuggestionSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  targetType: AutomationTargetTypeSchema,
  targetId: IdSchema,
  opportunityId: IdSchema.nullable(),
  applicationId: IdSchema.nullable(),
  artifactId: IdSchema.nullable(),
  actionType: AutomationActionTypeSchema,
  title: z.string().min(1),
  summary: z.string().min(1),
  reason: z.string().min(1),
  basis: z.string().min(1),
  confidence: z.string().min(1),
  sourceInputs: MetadataSchema,
  preview: AutomationPreviewSchema,
  status: AutomationSuggestionStatusSchema,
  expiresAt: IsoDateTimeSchema.nullable(),
  policyVersion: z.string().min(1),
  metadata: MetadataSchema,
});

export const AutomationApprovalLogSchema = ContractEnvelopeSchema.extend({
  id: IdSchema,
  workspaceId: IdSchema,
  suggestionId: IdSchema,
  actor: z.enum(["user", "system", "ai", "automation"]),
  targetType: AutomationTargetTypeSchema,
  targetId: IdSchema,
  actionType: AutomationActionTypeSchema,
  preview: AutomationPreviewSchema,
  previewHash: z.string().min(1),
  approvalStatus: AutomationApprovalStatusSchema,
  dismissalOrRejectionReason: z.string().nullable(),
  executionStatus: AutomationExecutionStatusSchema,
  executionResult: MetadataSchema,
  externalMutation: z.literal(false),
  policyVersion: z.string().min(1),
  createdAt: IsoDateTimeSchema,
  decidedAt: IsoDateTimeSchema.nullable(),
  executedAt: IsoDateTimeSchema.nullable(),
});

export const AutomationPreferencesSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  enabled: z.boolean().default(true),
  suggestionCategories: z.array(AutomationActionTypeSchema).default([]),
  followUpSuggestionDays: z.number().int().positive().default(7),
  artifactReadinessChecksEnabled: z.boolean().default(true),
  communicationDraftsEnabled: z.boolean().default(true),
  internalStateChangeSuggestionsEnabled: z.boolean().default(true),
  futureExternalActionsEnabled: z.literal(false),
  quietMode: z.boolean().default(false),
  policyVersion: z.string().min(1),
  metadata: MetadataSchema,
});

export type AutomationSuggestion = z.infer<typeof AutomationSuggestionSchema>;
export type AutomationApprovalLog = z.infer<typeof AutomationApprovalLogSchema>;
export type AutomationPreferences = z.infer<typeof AutomationPreferencesSchema>;
