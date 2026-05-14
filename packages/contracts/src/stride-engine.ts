import type { z } from "zod";

import type { Opportunity } from "./opportunity.js";
import { CONTRACT_VERSION, type ModelMetadata } from "./primitives.js";
import {
  type EvaluationSection,
  type StrideEvaluation,
  StrideEvaluationSchema,
} from "./stride-evaluation.js";
import type { Workspace } from "./workspace.js";

export const STRIDE_ENGINE_VERSION = "stride_engine_v1" as const;
export const STRIDE_PROMPT_VERSION = "stride_prompt_v1" as const;
export const STRIDE_RULESET_VERSION = "stride_rules_v1" as const;
export const STRIDE_EVALUATION_VERSION = "stride_evaluation_v1" as const;

export interface StrideEvaluationEngineInput {
  workspace: Workspace;
  opportunity: Opportunity;
  resumeProfileContent?: string | null;
  userContext?: Record<string, unknown>;
  evaluationId?: string;
  createdAt?: string;
  updatedAt?: string;
  modelProviderName?: string;
  modelName?: string;
  promptVersion?: string;
  rulesetVersion?: string;
  evaluationVersion?: string;
}

export interface StrideModelProviderResult {
  rawText: string;
  modelMetadata?: Partial<ModelMetadata>;
}

export interface StrideModelProvider {
  evaluate(prompt: string): Promise<StrideModelProviderResult>;
}

export interface StrideEvaluationEngineResult {
  status: "completed" | "failed";
  evaluation: StrideEvaluation;
  rawModelOutput: string | null;
  validationIssues: z.ZodIssue[];
  failureReason: string | null;
  usedFallback: boolean;
}

export interface StrideEvaluationPromptOptions {
  promptVersion?: string;
  rulesetVersion?: string;
}

export interface StrideEvaluationNormalizationMetadata {
  modelMetadata?: Partial<ModelMetadata>;
  rawModelOutput?: string | null;
  createdAt?: string;
  updatedAt?: string;
  promptVersion?: string;
  rulesetVersion?: string;
  evaluationVersion?: string;
  evaluationId?: string;
}

export interface StrideEvaluationFailure {
  reason: string;
  errorType?: string;
  validationIssues?: z.ZodIssue[];
  rawModelOutput?: string | null;
}

export async function evaluateStrideOpportunity(
  input: StrideEvaluationEngineInput,
  provider: StrideModelProvider,
  options: StrideEvaluationPromptOptions = {},
): Promise<StrideEvaluationEngineResult> {
  const prompt = buildStrideEvaluationPrompt(input, options);

  try {
    const providerResult = await provider.evaluate(prompt);
    const parsed = parseStrideModelOutput(providerResult.rawText);
    const normalized = normalizeStrideEvaluation(parsed, input, {
      modelMetadata: providerResult.modelMetadata,
      rawModelOutput: providerResult.rawText,
      promptVersion: options.promptVersion,
      rulesetVersion: options.rulesetVersion,
    });

    return {
      status: "completed",
      evaluation: normalized,
      rawModelOutput: providerResult.rawText,
      validationIssues: [],
      failureReason: null,
      usedFallback: false,
    };
  } catch (error) {
    const validationIssues = _extractValidationIssues(error);
    const rawModelOutput = _extractRawModelOutput(error);
    const fallback = buildDeterministicFallbackEvaluation(input, {
      reason: _safeFailureReason(error),
      errorType: error instanceof Error ? error.name : "UnknownError",
      validationIssues,
      rawModelOutput,
    });

    return {
      status: "failed",
      evaluation: fallback,
      rawModelOutput,
      validationIssues,
      failureReason: fallback.metadata.failureReason as string,
      usedFallback: true,
    };
  }
}

export function buildStrideEvaluationPrompt(
  input: StrideEvaluationEngineInput,
  options: StrideEvaluationPromptOptions = {},
): string {
  const promptVersion = options.promptVersion ?? input.promptVersion ?? STRIDE_PROMPT_VERSION;
  const rulesetVersion = options.rulesetVersion ?? input.rulesetVersion ?? STRIDE_RULESET_VERSION;
  const resumeContent = input.resumeProfileContent?.trim() || null;

  return [
    "You are CareerO's STRIDE evaluation engine.",
    `Prompt version: ${promptVersion}`,
    `Ruleset version: ${rulesetVersion}`,
    "",
    "Return strict JSON only. Do not wrap the response in Markdown.",
    "Do not generate resumes or cover letters.",
    "Do not invent candidate experience, resume facts, compensation facts, company facts, dates, or external research.",
    "Use only the supplied workspace, opportunity, user context, and resume/profile content.",
    "If resume/profile content is missing, mark affected sections as insufficient_data, lower confidence, and add an explicit assumption.",
    "",
    "Required output must validate against the canonical StrideEvaluation contract.",
    "Include: summary, role fit analysis through sections, strengths, gaps, risks, atsFindings, compensationFindings, remote compatibility, interview positioning in recommendations.nextActions, confidence, assumptions, modelMetadata, and version.",
    "",
    `Workspace JSON:\n${JSON.stringify(input.workspace, null, 2)}`,
    "",
    `Opportunity JSON:\n${JSON.stringify(input.opportunity, null, 2)}`,
    "",
    `User context JSON:\n${JSON.stringify(input.userContext ?? {}, null, 2)}`,
    "",
    `Resume/profile content:\n${resumeContent ?? "null"}`,
  ].join("\n");
}

export function parseStrideModelOutput(rawText: string): unknown {
  const jsonText = _extractJsonText(rawText);
  if (!jsonText) {
    throw new StrideModelOutputParseError("Model output did not contain a JSON object", rawText);
  }

  try {
    return JSON.parse(jsonText);
  } catch (error) {
    throw new StrideModelOutputParseError(
      error instanceof Error ? error.message : "Model output JSON parse failed",
      rawText,
    );
  }
}

export function normalizeStrideEvaluation(
  parsedOutput: unknown,
  input: StrideEvaluationEngineInput,
  metadata: StrideEvaluationNormalizationMetadata = {},
): StrideEvaluation {
  const now = _timestamp(metadata.createdAt ?? input.createdAt);
  const promptVersion =
    metadata.promptVersion ?? input.promptVersion ?? STRIDE_PROMPT_VERSION;
  const rulesetVersion =
    metadata.rulesetVersion ?? input.rulesetVersion ?? STRIDE_RULESET_VERSION;

  const candidate = {
    ...(typeof parsedOutput === "object" && parsedOutput !== null ? parsedOutput : {}),
    contractVersion: CONTRACT_VERSION,
    id: metadata.evaluationId ?? input.evaluationId ?? _randomUuid(),
    workspaceId: input.workspace.id,
    opportunityId: input.opportunity.id,
    version: {
      version:
        _readString(parsedOutput, ["version", "version"]) ??
        metadata.evaluationVersion ??
        input.evaluationVersion ??
        STRIDE_EVALUATION_VERSION,
      previousVersion: _readString(parsedOutput, ["version", "previousVersion"]),
      changeReason:
        _readString(parsedOutput, ["version", "changeReason"]) ??
        "Generated by the canonical STRIDE evaluation engine.",
    },
    status: "completed",
    modelMetadata: _modelMetadata(input, metadata.modelMetadata, promptVersion, rulesetVersion),
    reproducibility: {
      inputHash: _stableHash({
        workspace: input.workspace,
        opportunity: input.opportunity,
        resumeProfileContent: input.resumeProfileContent ?? null,
        userContext: input.userContext ?? {},
        promptVersion,
        rulesetVersion,
      }),
      roleContentHash: _stableHash(input.opportunity),
      sourceHash: input.resumeProfileContent ? _stableHash(input.resumeProfileContent) : null,
      promptVersion,
      rulesetVersion,
      sourceHashes: input.resumeProfileContent
        ? { resumeProfileContent: _stableHash(input.resumeProfileContent) }
        : {},
      deterministicBaseline: null,
    },
    createdAt: now,
    updatedAt: _timestamp(metadata.updatedAt ?? input.updatedAt ?? now),
    metadata: {
      ..._readRecord(parsedOutput, ["metadata"]),
      engineVersion: STRIDE_ENGINE_VERSION,
      rawModelOutputStoredSeparately: Boolean(metadata.rawModelOutput),
    },
  };

  const result = StrideEvaluationSchema.safeParse(candidate);
  if (!result.success) {
    throw new StrideEvaluationValidationError(result.error.issues, metadata.rawModelOutput ?? null);
  }

  return result.data;
}

export function buildDeterministicFallbackEvaluation(
  input: StrideEvaluationEngineInput,
  failure: StrideEvaluationFailure,
): StrideEvaluation {
  const now = _timestamp(input.createdAt);
  const promptVersion = input.promptVersion ?? STRIDE_PROMPT_VERSION;
  const rulesetVersion = input.rulesetVersion ?? STRIDE_RULESET_VERSION;
  const hasResume = Boolean(input.resumeProfileContent?.trim());
  const noResumeAssumption =
    "No resume/profile content was supplied; candidate-specific fit is marked as insufficient_data.";

  return StrideEvaluationSchema.parse({
    contractVersion: CONTRACT_VERSION,
    id: input.evaluationId ?? _randomUuid(),
    workspaceId: input.workspace.id,
    opportunityId: input.opportunity.id,
    version: {
      version: input.evaluationVersion ?? STRIDE_EVALUATION_VERSION,
      previousVersion: null,
      changeReason: "Deterministic fallback after STRIDE engine failure.",
    },
    status: "failed",
    modelMetadata: _modelMetadata(input, null, promptVersion, rulesetVersion),
    summary:
      "STRIDE evaluation could not be completed with a validated model response. A conservative fallback record was produced for auditability.",
    overallScore: null,
    strengths: [],
    gaps: [
      {
        label: "Validated evaluation unavailable",
        score: null,
        evidence: [],
        notes: failure.reason,
      },
    ],
    risks: [
      {
        label: "Evaluation requires review",
        score: null,
        evidence: [],
        notes: "Do not treat this failed fallback as a completed STRIDE recommendation.",
      },
    ],
    atsFindings: {
      matchedKeywords: [],
      missingKeywords: [],
      keywordNotes: "ATS analysis was not completed.",
      score: null,
    },
    compensationFindings: {
      status: input.opportunity.compensation ? "needs_review" : "unknown",
      notes: input.opportunity.compensation
        ? "Compensation was present but not fully evaluated."
        : "No compensation evaluation was completed.",
      evidence: input.opportunity.compensation?.sourceText
        ? [input.opportunity.compensation.sourceText]
        : [],
      score: null,
    },
    recommendations: {
      decision: "needs_review",
      rationale: "The model output was unavailable or invalid, so a human review is required.",
      nextActions: [
        "Review opportunity details manually.",
        "Re-run STRIDE evaluation when model output can be validated.",
      ],
    },
    confidence: {
      level: "low",
      score: hasResume ? 0.25 : 0.15,
      rationale: hasResume
        ? "Fallback confidence is low because the model result was not validated."
        : "Fallback confidence is low because resume/profile content is missing and the model result was not validated.",
    },
    sections: {
      strategicFit: _fallbackSection("Strategic fit was not evaluated."),
      technicalAlignment: _fallbackSection("Technical alignment was not evaluated."),
      seniorityAlignment: _fallbackSection("Seniority alignment was not evaluated."),
      compensationAlignment: _fallbackSection("Compensation alignment was not evaluated."),
      remoteAlignment: _fallbackSection("Remote compatibility was not evaluated."),
      companyRisk: _fallbackSection("Company risk was not evaluated."),
      applicationEffort: _fallbackSection("Application effort was not evaluated."),
      atsResumeAlignment: _fallbackSection("ATS/resume alignment was not evaluated."),
    },
    assumptions: [
      "No external research was performed.",
      "No resume or cover letter was generated.",
      ...(hasResume ? [] : [noResumeAssumption]),
      `Fallback reason: ${failure.reason}`,
    ],
    reproducibility: {
      inputHash: _stableHash({
        workspace: input.workspace,
        opportunity: input.opportunity,
        resumeProfileContent: input.resumeProfileContent ?? null,
        userContext: input.userContext ?? {},
        promptVersion,
        rulesetVersion,
      }),
      roleContentHash: _stableHash(input.opportunity),
      sourceHash: input.resumeProfileContent ? _stableHash(input.resumeProfileContent) : null,
      promptVersion,
      rulesetVersion,
      sourceHashes: input.resumeProfileContent
        ? { resumeProfileContent: _stableHash(input.resumeProfileContent) }
        : {},
      deterministicBaseline: {
        engineVersion: STRIDE_ENGINE_VERSION,
        fallback: true,
      },
    },
    metadata: {
      engineVersion: STRIDE_ENGINE_VERSION,
      failureReason: failure.reason,
      errorType: failure.errorType ?? null,
      validationIssues: failure.validationIssues?.map((issue) => ({
        path: issue.path.join("."),
        message: issue.message,
      })) ?? [],
      rawModelOutputStoredSeparately: Boolean(failure.rawModelOutput),
    },
    createdAt: now,
    updatedAt: _timestamp(input.updatedAt ?? now),
  });
}

export class StrideModelOutputParseError extends Error {
  constructor(
    message: string,
    public readonly rawModelOutput: string,
  ) {
    super(message);
    this.name = "StrideModelOutputParseError";
  }
}

export class StrideEvaluationValidationError extends Error {
  constructor(
    public readonly issues: z.ZodIssue[],
    public readonly rawModelOutput: string | null,
  ) {
    super("Model output did not validate against StrideEvaluationSchema");
    this.name = "StrideEvaluationValidationError";
  }
}

function _fallbackSection(summary: string): EvaluationSection {
  return {
    status: "insufficient_data",
    score: null,
    summary,
    evidence: [],
    gaps: ["Validated model output was unavailable."],
    assumptions: ["Human review is required."],
  };
}

function _modelMetadata(
  input: StrideEvaluationEngineInput,
  override: Partial<ModelMetadata> | null | undefined,
  promptVersion: string,
  rulesetVersion: string,
): ModelMetadata {
  return {
    provider: override?.provider ?? input.modelProviderName ?? "injected_provider",
    model: override?.model ?? input.modelName ?? "unspecified",
    promptVersion: override?.promptVersion ?? promptVersion,
    rulesetVersion: override?.rulesetVersion ?? rulesetVersion,
    inputTokenEstimate: override?.inputTokenEstimate ?? null,
    outputTokenEstimate: override?.outputTokenEstimate ?? null,
    latencyMs: override?.latencyMs ?? null,
  };
}

function _extractJsonText(rawText: string): string | null {
  const trimmed = rawText.trim();
  if (!trimmed) {
    return null;
  }

  const fenced = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced?.[1]) {
    return fenced[1].trim();
  }

  const firstBrace = trimmed.indexOf("{");
  const lastBrace = trimmed.lastIndexOf("}");
  if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
    return null;
  }

  return trimmed.slice(firstBrace, lastBrace + 1);
}

function _extractValidationIssues(error: unknown): z.ZodIssue[] {
  if (error instanceof StrideEvaluationValidationError) {
    return error.issues;
  }
  return [];
}

function _extractRawModelOutput(error: unknown): string | null {
  if (error instanceof StrideEvaluationValidationError) {
    return error.rawModelOutput;
  }
  if (error instanceof StrideModelOutputParseError) {
    return error.rawModelOutput;
  }
  return null;
}

function _safeFailureReason(error: unknown): string {
  if (error instanceof Error) {
    return error.message.slice(0, 240);
  }
  return "STRIDE evaluation failed".slice(0, 240);
}

function _timestamp(value?: string | null): string {
  return value ?? new Date().toISOString();
}

function _readString(source: unknown, path: string[]): string | null {
  let current: unknown = source;
  for (const segment of path) {
    if (typeof current !== "object" || current === null || !(segment in current)) {
      return null;
    }
    current = (current as Record<string, unknown>)[segment];
  }
  return typeof current === "string" ? current : null;
}

function _readRecord(source: unknown, path: string[]): Record<string, unknown> {
  let current: unknown = source;
  for (const segment of path) {
    if (typeof current !== "object" || current === null || !(segment in current)) {
      return {};
    }
    current = (current as Record<string, unknown>)[segment];
  }
  return typeof current === "object" && current !== null && !Array.isArray(current)
    ? (current as Record<string, unknown>)
    : {};
}

function _stableHash(value: unknown): string {
  const input = JSON.stringify(_sortForHash(value));
  let hash = 5381;
  for (let index = 0; index < input.length; index += 1) {
    hash = (hash * 33) ^ input.charCodeAt(index);
  }
  return `hash:${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

function _sortForHash(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(_sortForHash);
  }
  if (typeof value === "object" && value !== null) {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, item]) => [key, _sortForHash(item)]),
    );
  }
  return value;
}

function _randomUuid(): string {
  const randomValues = Array.from({ length: 16 }, () => Math.floor(Math.random() * 256));
  randomValues[6] = (randomValues[6] & 0x0f) | 0x40;
  randomValues[8] = (randomValues[8] & 0x3f) | 0x80;
  const hex = randomValues.map((value) => value.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
