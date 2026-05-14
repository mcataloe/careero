import { z } from "zod";

import { ApplicationWorkflowStateSchema } from "./enums.js";
import {
  AuditTimestampsSchema,
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  LinkSchema,
  MetadataSchema,
} from "./primitives.js";

export const ApplicationStateHistoryEntrySchema = z.object({
  state: ApplicationWorkflowStateSchema,
  changedAt: IsoDateTimeSchema,
  changedBy: z.enum(["user", "system", "automation"]).default("user"),
  reason: z.string().nullable(),
  metadata: MetadataSchema,
});

export const ApplicationReminderSchema = z.object({
  id: IdSchema,
  dueAt: IsoDateTimeSchema,
  title: z.string().min(1),
  notes: z.string().nullable(),
  completedAt: IsoDateTimeSchema.nullable(),
});

export const ApplicationNoteSchema = z.object({
  id: IdSchema,
  createdAt: IsoDateTimeSchema,
  author: z.string().nullable(),
  body: z.string().min(1),
});

export const InterviewStageSchema = z.object({
  id: IdSchema,
  stageType: z.enum(["recruiter_screen", "hiring_manager", "technical", "panel", "onsite", "offer", "other"]),
  title: z.string().min(1),
  status: z.enum(["scheduled", "completed", "cancelled", "pending", "declined"]),
  scheduledAt: IsoDateTimeSchema.nullable(),
  completedAt: IsoDateTimeSchema.nullable(),
  notes: z.string().nullable(),
  externalLinks: z.array(LinkSchema).default([]),
});

export const ApplicationStateSchema = ContractEnvelopeSchema.merge(AuditTimestampsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  opportunityId: IdSchema,
  currentState: ApplicationWorkflowStateSchema,
  stateHistory: z.array(ApplicationStateHistoryEntrySchema).min(1),
  reminders: z.array(ApplicationReminderSchema).default([]),
  notes: z.array(ApplicationNoteSchema).default([]),
  interviewStages: z.array(InterviewStageSchema).default([]),
  externalLinks: z.array(LinkSchema).default([]),
  applicationMetadata: MetadataSchema,
});

export type ApplicationState = z.infer<typeof ApplicationStateSchema>;
