import { describe, expect, it } from "vitest";

import {
  type Opportunity,
  type CompassEvaluation,
  buildDeterministicFallbackEvaluation,
  buildCompassEvaluationPrompt,
  canonicalExamples,
  evaluateCompassOpportunity,
  normalizeCompassEvaluation,
  parseCompassModelOutput,
} from "../src/index.js";

const engineInput = {
  workspace: canonicalExamples.Workspace,
  opportunity: canonicalExamples.Opportunity,
  resumeProfileContent: "Built Python platform services, led engineering teams, and managed PostgreSQL systems.",
  userContext: { targetKeywords: ["Python", "PostgreSQL", "platform"] },
  evaluationId: canonicalExamples.CompassEvaluation.id,
  createdAt: canonicalExamples.CompassEvaluation.createdAt,
  updatedAt: canonicalExamples.CompassEvaluation.updatedAt,
  modelProviderName: "fake",
  modelName: "fake-model",
};

function completedEvaluation(overrides: Partial<CompassEvaluation> = {}): CompassEvaluation {
  return {
    ...canonicalExamples.CompassEvaluation,
    ...overrides,
    status: "completed",
    id: canonicalExamples.CompassEvaluation.id,
    workspaceId: canonicalExamples.Workspace.id,
    opportunityId: canonicalExamples.Opportunity.id,
  };
}

describe("COMPASS prompt builder", () => {
  it("includes workspace, opportunity, resume profile content, and grounding rules", () => {
    const prompt = buildCompassEvaluationPrompt(engineInput);

    expect(prompt).toContain(canonicalExamples.Workspace.title);
    expect(prompt).toContain(canonicalExamples.Opportunity.title);
    expect(prompt).toContain("Built Python platform services");
    expect(prompt).toContain("Do not invent candidate experience");
    expect(prompt).toContain("Do not generate resumes or cover letters");
    expect(prompt).toContain("Return strict JSON only");
  });

  it("handles missing resume context and records confidence impact instructions", () => {
    const prompt = buildCompassEvaluationPrompt({
      ...engineInput,
      resumeProfileContent: null,
    });

    expect(prompt).toContain("Resume/profile content:\nnull");
    expect(prompt).toContain("mark affected sections as insufficient_data");
    expect(prompt).toContain("lower confidence");
  });
});

describe("COMPASS model output parsing and validation", () => {
  it("parses JSON from plain or fenced model output", () => {
    expect(parseCompassModelOutput(JSON.stringify({ summary: "ok" }))).toEqual({ summary: "ok" });
    expect(parseCompassModelOutput("```json\n{\"summary\":\"ok\"}\n```")).toEqual({ summary: "ok" });
  });

  it("normalizes valid model output into a completed canonical evaluation", () => {
    const evaluation = normalizeCompassEvaluation(completedEvaluation(), engineInput, {
      modelMetadata: {
        provider: "fake",
        model: "fake-model",
        inputTokenEstimate: 100,
        outputTokenEstimate: 50,
        latencyMs: 25,
      },
      rawModelOutput: JSON.stringify(completedEvaluation()),
    });

    expect(evaluation.status).toBe("completed");
    expect(evaluation.workspaceId).toBe(engineInput.workspace.id);
    expect(evaluation.opportunityId).toBe(engineInput.opportunity.id);
    expect(evaluation.modelMetadata.provider).toBe("fake");
    expect(evaluation.metadata.rawModelOutputStoredSeparately).toBe(true);
  });
});

describe("COMPASS engine execution", () => {
  it("returns a completed evaluation for valid fake provider output", async () => {
    const rawText = JSON.stringify(completedEvaluation());
    const result = await evaluateCompassOpportunity(engineInput, {
      evaluate: async () => ({
        rawText,
        modelMetadata: {
          provider: "fake",
          model: "fake-model",
          inputTokenEstimate: 120,
          outputTokenEstimate: 80,
          latencyMs: 12,
        },
      }),
    });

    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(false);
    expect(result.rawModelOutput).toBe(rawText);
    expect(result.validationIssues).toEqual([]);
    expect(result.evaluation.status).toBe("completed");
  });

  it("returns a failed fallback for malformed model JSON", async () => {
    const result = await evaluateCompassOpportunity(engineInput, {
      evaluate: async () => ({ rawText: "not json" }),
    });

    expect(result.status).toBe("failed");
    expect(result.usedFallback).toBe(true);
    expect(result.evaluation.status).toBe("failed");
    expect(result.rawModelOutput).toBe("not json");
    expect(result.failureReason).toContain("JSON object");
  });

  it("returns a failed fallback with validation issues for schema-invalid output", async () => {
    const invalid = { ...completedEvaluation(), confidence: { level: "certain" } };
    const result = await evaluateCompassOpportunity(engineInput, {
      evaluate: async () => ({ rawText: JSON.stringify(invalid) }),
    });

    expect(result.status).toBe("failed");
    expect(result.usedFallback).toBe(true);
    expect(result.evaluation.status).toBe("failed");
    expect(result.validationIssues.length).toBeGreaterThan(0);
    expect(result.evaluation.metadata.validationIssues).toBeDefined();
  });

  it("returns a failed fallback when provider throws", async () => {
    const result = await evaluateCompassOpportunity(engineInput, {
      evaluate: async () => {
        throw new Error("provider unavailable");
      },
    });

    expect(result.status).toBe("failed");
    expect(result.usedFallback).toBe(true);
    expect(result.rawModelOutput).toBeNull();
    expect(result.failureReason).toBe("provider unavailable");
  });

  it("marks missing resume context in deterministic fallback assumptions", () => {
    const fallback = buildDeterministicFallbackEvaluation(
      { ...engineInput, resumeProfileContent: null },
      { reason: "test failure" },
    );

    expect(fallback.status).toBe("failed");
    expect(fallback.confidence.level).toBe("low");
    expect(fallback.assumptions.join(" ")).toContain("No resume/profile content was supplied");
  });
});

describe("COMPASS representative fixtures", () => {
  it("builds a valid fallback for an ambiguous sparse opportunity", () => {
    const sparseOpportunity: Opportunity = {
      ...canonicalExamples.Opportunity,
      rawContent: null,
      normalizedContent: {
        description: null,
        responsibilities: [],
        requirements: [],
        skills: [],
        seniority: null,
        notes: null,
      },
      compensation: null,
      remoteMode: "unspecified",
      parseConfidence: {},
    };

    const fallback = buildDeterministicFallbackEvaluation(
      { ...engineInput, opportunity: sparseOpportunity, resumeProfileContent: null },
      { reason: "sparse fixture fallback" },
    );

    expect(fallback.status).toBe("failed");
    expect(fallback.compensationFindings.status).toBe("unknown");
    expect(fallback.sections.atsResumeAlignment.status).toBe("insufficient_data");
  });

  it("builds a valid fallback for a risky opportunity", () => {
    const riskyOpportunity: Opportunity = {
      ...canonicalExamples.Opportunity,
      title: "Commission Only Growth Hacker",
      normalizedContent: {
        ...canonicalExamples.Opportunity.normalizedContent,
        description: "Fast-paced vague responsibilities with unclear compensation.",
      },
      compensation: null,
      tags: ["risk"],
    };

    const fallback = buildDeterministicFallbackEvaluation(
      { ...engineInput, opportunity: riskyOpportunity },
      { reason: "risky fixture fallback" },
    );

    expect(fallback.status).toBe("failed");
    expect(fallback.recommendations?.decision).toBe("needs_review");
    expect(fallback.risks[0]?.label).toBe("Evaluation requires review");
  });
});
