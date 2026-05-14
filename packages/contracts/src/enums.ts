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
  "greenhouse",
  "lever",
  "ashby",
  "workable",
  "company_site",
  "recruiter_email",
  "job_board",
  "referral",
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

export type WorkspaceStatus = z.infer<typeof WorkspaceStatusSchema>;
export type OpportunityStatus = z.infer<typeof OpportunityStatusSchema>;
export type ApplicationWorkflowState = z.infer<typeof ApplicationWorkflowStateSchema>;
export type RemoteType = z.infer<typeof RemoteTypeSchema>;
export type EmploymentType = z.infer<typeof EmploymentTypeSchema>;
export type Recommendation = z.infer<typeof RecommendationSchema>;
export type ConfidenceLevel = z.infer<typeof ConfidenceLevelSchema>;
