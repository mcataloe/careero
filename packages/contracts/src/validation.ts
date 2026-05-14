import type { z } from "zod";

import { ApplicationStateSchema } from "./application-state.js";
import { CoverLetterArtifactSchema, ResumeArtifactSchema } from "./artifacts.js";
import { OpportunitySchema } from "./opportunity.js";
import { StrideEvaluationSchema } from "./stride-evaluation.js";
import { WorkspaceSchema } from "./workspace.js";

export type ContractValidationResult<T> =
  | { success: true; data: T }
  | { success: false; issues: z.ZodIssue[] };

export function validateContract<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  value: unknown,
): ContractValidationResult<z.infer<TSchema>> {
  const result = schema.safeParse(value);

  if (result.success) {
    return { success: true, data: result.data };
  }

  return { success: false, issues: result.error.issues };
}

export function parseContract<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  value: unknown,
): z.infer<TSchema> {
  return schema.parse(value);
}

export const parseWorkspace = (value: unknown) => parseContract(WorkspaceSchema, value);
export const parseOpportunity = (value: unknown) => parseContract(OpportunitySchema, value);
export const parseStrideEvaluation = (value: unknown) => parseContract(StrideEvaluationSchema, value);
export const parseResumeArtifact = (value: unknown) => parseContract(ResumeArtifactSchema, value);
export const parseCoverLetterArtifact = (value: unknown) => parseContract(CoverLetterArtifactSchema, value);
export const parseApplicationState = (value: unknown) => parseContract(ApplicationStateSchema, value);

export const validateWorkspace = (value: unknown) => validateContract(WorkspaceSchema, value);
export const validateOpportunity = (value: unknown) => validateContract(OpportunitySchema, value);
export const validateStrideEvaluation = (value: unknown) => validateContract(StrideEvaluationSchema, value);
export const validateResumeArtifact = (value: unknown) => validateContract(ResumeArtifactSchema, value);
export const validateCoverLetterArtifact = (value: unknown) => validateContract(CoverLetterArtifactSchema, value);
export const validateApplicationState = (value: unknown) => validateContract(ApplicationStateSchema, value);
