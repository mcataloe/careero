import { z } from "zod";

import { ApplicationWorkflowStateSchema } from "./enums.js";
import {
  ContractEnvelopeSchema,
  IdSchema,
  IsoDateTimeSchema,
  LinkSchema,
  MetadataSchema,
  TimestampFieldsSchema,
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

export const ApplicationInterviewStageTypeSchema = z.enum([
  "recruiter_screen",
  "hiring_manager",
  "technical",
  "system_design",
  "behavioral",
  "panel",
  "final",
  "offer_discussion",
  "other",
]);

export const ApplicationInterviewStatusSchema = z.enum([
  "planned",
  "scheduled",
  "completed",
  "canceled",
  "no_show",
]);

export const ApplicationInterviewStageSchema = z.object({
  id: IdSchema,
  stageType: ApplicationInterviewStageTypeSchema,
  title: z.string().min(1),
  scheduledAt: IsoDateTimeSchema.nullable(),
  completedAt: IsoDateTimeSchema.nullable(),
  status: ApplicationInterviewStatusSchema,
  interviewerNames: z.array(z.string()).default([]),
  locationOrMeetingLink: z.string().nullable(),
  notes: z.string().nullable(),
  preparationNotes: z.string().nullable(),
  outcomeNotes: z.string().nullable(),
  metadata: MetadataSchema,
});

export const ApplicationStateSchema = ContractEnvelopeSchema.merge(TimestampFieldsSchema).extend({
  id: IdSchema,
  workspaceId: IdSchema,
  opportunityId: IdSchema,
  currentState: ApplicationWorkflowStateSchema,
  stateHistory: z.array(ApplicationStateHistoryEntrySchema).min(1),
  reminders: z.array(ApplicationReminderSchema).default([]),
  notes: z.array(ApplicationNoteSchema).default([]),
  interviewStages: z.array(ApplicationInterviewStageSchema).default([]),
  externalLinks: z.array(LinkSchema).default([]),
  metadata: MetadataSchema,
});

export type ApplicationState = z.infer<typeof ApplicationStateSchema>;
