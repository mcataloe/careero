import { z } from "zod";

export const WorkspaceStatusSchema = z.enum(["active", "paused", "archived", "completed"]);
export const WorkspaceSearchCategorySchema = z.enum([
  "full_time_leadership",
  "full_time_individual_contributor",
  "contract_consulting",
  "exploration",
  "relocation",
  "other",
]);

export const OpportunitySourceTypeSchema = z.enum([
  "manual",
  "linkedin_manual",
  "linkedin",
  "recruiter",
  "greenhouse",
  "lever",
  "ashby",
  "workable",
  "company_site",
  "recruiter_email",
  "job_board",
  "referral",
  "networking",
  "direct_outreach",
  "internal_referral",
  "other",
]);

export const RemoteTypeSchema = z.enum(["remote", "hybrid", "onsite", "unspecified"]);
export const EmploymentTypeSchema = z.enum([
  "full_time",
  "part_time",
  "contract",
  "consulting",
  "fractional",
  "internship",
  "temporary",
  "other",
  "unspecified",
]);

export const OpportunityStatusSchema = z.enum([
  "discovered",
  "interested",
  "evaluating",
  "evaluated",
  "application_started",
  "applied",
  "rejected",
  "withdrawn",
  "archived",
]);

export const EvaluationStatusSchema = z.enum(["pending", "completed", "failed", "superseded"]);
export const RecommendationSchema = z.enum(["apply", "monitor", "skip", "needs_review"]);
export const ConfidenceLevelSchema = z.enum(["low", "medium", "high"]);

export const ArtifactLifecycleStatusSchema = z.enum([
  "draft",
  "reviewed",
  "approved",
  "exported",
  "archived",
]);

export const ResumeArtifactTypeSchema = z.enum([
  "source_resume",
  "master_resume",
  "resume_variant",
  "tailored_resume",
  "uploaded_resume",
]);

export const ArtifactSourceTypeSchema = z.enum(["uploaded", "generated", "imported", "manual"]);

export const CoverLetterToneSchema = z.enum([
  "direct",
  "warm",
  "executive",
  "technical",
  "consultative",
  "custom",
]);

export const ExportFormatSchema = z.enum(["pdf", "docx", "md", "txt", "html"]);

export const ApplicationWorkflowStateSchema = z.enum([
  "discovered",
  "interested",
  "applied",
  "interviewing",
  "offer",
  "rejected",
  "withdrawn",
  "archived",
]);

export const AutomationActionTypeSchema = z.enum([
  "follow_up_suggestion",
  "reminder_suggestion",
  "artifact_readiness_check",
  "communication_draft",
  "workflow_state_suggestion",
  "opportunity_review_suggestion",
  "future_external_action_disabled",
]);

export const AutomationTargetTypeSchema = z.enum([
  "workspace",
  "opportunity",
  "application",
  "artifact",
  "reminder",
]);

export const AutomationSuggestionStatusSchema = z.enum([
  "active",
  "dismissed",
  "rejected",
  "approved",
  "expired",
]);

export const AutomationApprovalStatusSchema = z.enum([
  "pending",
  "approved",
  "rejected",
  "dismissed",
  "expired",
]);

export const AutomationExecutionStatusSchema = z.enum([
  "not_applicable",
  "pending",
  "succeeded",
  "failed",
  "canceled",
]);

export type WorkspaceStatus = z.infer<typeof WorkspaceStatusSchema>;
export type OpportunityStatus = z.infer<typeof OpportunityStatusSchema>;
export type ApplicationWorkflowState = z.infer<typeof ApplicationWorkflowStateSchema>;
export type RemoteType = z.infer<typeof RemoteTypeSchema>;
export type EmploymentType = z.infer<typeof EmploymentTypeSchema>;
export type Recommendation = z.infer<typeof RecommendationSchema>;
export type ConfidenceLevel = z.infer<typeof ConfidenceLevelSchema>;
export type AutomationActionType = z.infer<typeof AutomationActionTypeSchema>;
export type AutomationTargetType = z.infer<typeof AutomationTargetTypeSchema>;
export type AutomationSuggestionStatus = z.infer<typeof AutomationSuggestionStatusSchema>;
export type AutomationApprovalStatus = z.infer<typeof AutomationApprovalStatusSchema>;
export type AutomationExecutionStatus = z.infer<typeof AutomationExecutionStatusSchema>;
