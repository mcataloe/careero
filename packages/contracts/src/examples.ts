import type { ApplicationState } from "./application-state.js";
import type { CoverLetterArtifact, ResumeArtifact } from "./artifacts.js";
import type { Opportunity } from "./opportunity.js";
import { CONTRACT_VERSION } from "./primitives.js";
import type { StrideEvaluation } from "./stride-evaluation.js";
import type { Workspace } from "./workspace.js";

const now = "2026-05-13T18:00:00.000Z";
const userId = "11111111-1111-4111-8111-111111111111";
const workspaceId = "22222222-2222-4222-8222-222222222222";
const opportunityId = "33333333-3333-4333-8333-333333333333";
const evaluationId = "44444444-4444-4444-8444-444444444444";
const resumeArtifactId = "55555555-5555-4555-8555-555555555555";
const coverLetterArtifactId = "66666666-6666-4666-8666-666666666666";
const applicationStateId = "77777777-7777-4777-8777-777777777777";

export const workspaceExample: Workspace = {
  contractVersion: CONTRACT_VERSION,
  id: workspaceId,
  userId,
  title: "Full-time leadership search",
  description: "Search for senior engineering leadership roles.",
  workspaceType: "full_time_leadership",
  status: "active",
  preferences: {
    targetTitles: ["Director of Engineering", "VP Engineering"],
    targetSeniority: ["director", "executive"],
    preferredRemoteTypes: ["remote", "hybrid"],
    preferredLocations: ["Chicago", "Remote US"],
    targetCompensation: {
      min: 180000,
      max: 240000,
      currency: "USD",
      period: "annual",
      sourceText: "$180k-$240k annual",
    },
    targetKeywords: ["platform", "engineering leadership", "AI"],
    avoidKeywords: ["commission only"],
    notes: "Prioritize credible product and platform teams.",
  },
  aiContextSummary: "Candidate is targeting engineering leadership roles.",
  tags: ["leadership", "full-time"],
  metadata: {},
  createdAt: now,
  updatedAt: now,
  archivedAt: null,
};

export const opportunityExample: Opportunity = {
  contractVersion: CONTRACT_VERSION,
  id: opportunityId,
  workspaceId,
  sourceType: "linkedin_manual",
  sourceUrl: "https://example.com/jobs/123",
  rawContent: "Example Systems is hiring a Senior Platform Engineering Manager...",
  normalizedContent: {
    description: "Lead platform engineering teams and improve delivery systems.",
    responsibilities: ["Lead platform teams", "Improve engineering delivery"],
    requirements: ["Engineering management", "Cloud platforms"],
    skills: ["Python", "PostgreSQL", "AWS"],
    seniority: "senior",
    notes: "Parsed from manually supplied job posting content.",
  },
  company: {
    name: "Example Systems",
    websiteUrl: "https://example.com",
    industry: "SaaS",
    notes: null,
  },
  title: "Senior Platform Engineering Manager",
  employmentType: "full_time",
  compensation: {
    min: 170000,
    max: 220000,
    currency: "USD",
    period: "annual",
    sourceText: "$170k-$220k",
  },
  location: {
    label: "Chicago, IL",
    city: "Chicago",
    region: "IL",
    country: "US",
    timezone: "America/Chicago",
  },
  remoteMode: "hybrid",
  parseConfidence: { title: 0.96, company: 0.94 },
  tags: ["platform", "leadership"],
  status: "interested",
  metadata: {},
  createdAt: now,
  updatedAt: now,
};

export const strideEvaluationExample: StrideEvaluation = {
  contractVersion: CONTRACT_VERSION,
  id: evaluationId,
  workspaceId,
  opportunityId,
  version: {
    version: "stride_evaluation_v1",
    previousVersion: null,
    changeReason: "Initial canonical evaluation contract.",
  },
  status: "completed",
  modelMetadata: {
    provider: "openai",
    model: "gpt-5-mini",
    promptVersion: "stride_prompt_v1",
    rulesetVersion: "stride_rules_v1",
    inputTokenEstimate: 1800,
    outputTokenEstimate: 900,
    latencyMs: 1200,
  },
  summary: "The opportunity appears directionally aligned with platform leadership goals.",
  overallScore: 78,
  strengths: [{ label: "Leadership alignment", score: 0.82, evidence: ["Lead platform teams"], notes: null }],
  gaps: [{ label: "Company risk", score: 0.4, evidence: [], notes: "Limited company context supplied." }],
  risks: [{ label: "Hybrid requirement", score: 0.3, evidence: ["Chicago hybrid"], notes: null }],
  atsFindings: {
    matchedKeywords: ["platform", "PostgreSQL"],
    missingKeywords: ["AI strategy"],
    keywordNotes: "Keyword coverage is partial.",
    score: 72,
  },
  compensationFindings: {
    status: "aligned",
    notes: "Posted range overlaps target compensation.",
    evidence: ["$170k-$220k"],
    score: 80,
  },
  recommendations: {
    decision: "apply",
    rationale: "The role has enough alignment to justify applying after review.",
    nextActions: ["Review hybrid expectations", "Tailor resume to platform leadership"],
  },
  confidence: {
    level: "medium",
    score: 0.72,
    rationale: "Role and compensation data are available, but company context is limited.",
  },
  sections: {
    strategicFit: { status: "strong_match", score: 82, summary: "Aligned to platform leadership.", evidence: ["Lead platform teams"], gaps: [], assumptions: [] },
    technicalAlignment: { status: "partial_match", score: 72, summary: "Core technical themes are present.", evidence: ["Python", "PostgreSQL"], gaps: ["AI strategy"], assumptions: [] },
    seniorityAlignment: { status: "strong_match", score: 84, summary: "Management seniority appears aligned.", evidence: ["Engineering Manager"], gaps: [], assumptions: [] },
    compensationAlignment: { status: "strong_match", score: 80, summary: "Range overlaps target.", evidence: ["$170k-$220k"], gaps: [], assumptions: [] },
    remoteAlignment: { status: "partial_match", score: 65, summary: "Hybrid may need review.", evidence: ["Chicago hybrid"], gaps: [], assumptions: [] },
    companyRisk: { status: "insufficient_data", score: null, summary: "Limited company details supplied.", evidence: [], gaps: ["No company research yet"], assumptions: [] },
    applicationEffort: { status: "partial_match", score: 70, summary: "Likely requires focused tailoring.", evidence: [], gaps: [], assumptions: [] },
    atsResumeAlignment: { status: "partial_match", score: 72, summary: "Some keyword alignment.", evidence: ["platform", "PostgreSQL"], gaps: ["AI strategy"], assumptions: [] },
  },
  assumptions: ["No external research was used."],
  reproducibility: {
    inputHash: "sha256:evaluation-input",
    roleContentHash: "sha256:role-content",
    sourceHash: "sha256:resume-source",
    promptVersion: "stride_prompt_v1",
    rulesetVersion: "stride_rules_v1",
    sourceHashes: { resume: "sha256:resume-source" },
    deterministicBaseline: { score: 78 },
  },
  metadata: {},
  createdAt: now,
  updatedAt: now,
};

export const resumeArtifactExample: ResumeArtifact = {
  contractVersion: CONTRACT_VERSION,
  id: resumeArtifactId,
  workspaceId,
  opportunityId,
  sourceArtifactId: null,
  artifactType: "tailored_resume",
  title: "Example Systems tailored resume",
  content: "Resume content prepared for Example Systems.",
  formatMetadata: {
    primaryFormat: "md",
    availableFormats: ["md", "pdf", "docx"],
    contentHash: "sha256:resume-artifact",
  },
  generationMetadata: {
    generatedBy: "ai",
    modelMetadata: strideEvaluationExample.modelMetadata,
    promptVersion: "resume_artifact_prompt_v1",
    inputHash: "sha256:resume-input",
    groundingSourceIds: [],
    warnings: [],
  },
  exportMetadata: [{ format: "pdf", exportedAt: null, fileName: null, contentHash: null }],
  revision: {
    revisionId: "88888888-8888-4888-8888-888888888888",
    parentArtifactId: null,
    revisionNumber: 1,
    changeSummary: "Initial tailored resume artifact.",
    createdAt: now,
  },
  uploadMetadata: null,
  parsingMetadata: null,
  tailoringNotes: "Emphasize platform leadership.",
  metadata: {},
  createdAt: now,
  updatedAt: now,
};

export const coverLetterArtifactExample: CoverLetterArtifact = {
  contractVersion: CONTRACT_VERSION,
  id: coverLetterArtifactId,
  workspaceId,
  opportunityId,
  title: "Example Systems cover letter",
  content: "Cover letter content prepared for Example Systems.",
  tone: "direct",
  generationMetadata: {
    generatedBy: "ai",
    modelMetadata: strideEvaluationExample.modelMetadata,
    promptVersion: "cover_letter_prompt_v1",
    inputHash: "sha256:cover-letter-input",
    groundingSourceIds: [],
    warnings: [],
  },
  editHistory: [{ editedAt: now, editedBy: "user", summary: "Reviewed opening paragraph." }],
  exportMetadata: [{ format: "docx", exportedAt: null, fileName: null, contentHash: null }],
  revision: {
    revisionId: "99999999-9999-4999-8999-999999999999",
    parentArtifactId: null,
    revisionNumber: 1,
    changeSummary: "Initial cover letter artifact.",
    createdAt: now,
  },
  metadata: {},
  createdAt: now,
  updatedAt: now,
};

export const applicationStateExample: ApplicationState = {
  contractVersion: CONTRACT_VERSION,
  id: applicationStateId,
  workspaceId,
  opportunityId,
  currentState: "interested",
  stateHistory: [
    {
      state: "discovered",
      changedAt: now,
      changedBy: "user",
      reason: "Opportunity pasted into Careero.",
      metadata: {},
    },
    {
      state: "interested",
      changedAt: now,
      changedBy: "user",
      reason: "STRIDE baseline recommended applying.",
      metadata: {},
    },
  ],
  reminders: [
    {
      id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      dueAt: "2026-05-20T15:00:00.000Z",
      title: "Decide whether to apply",
      notes: null,
      completedAt: null,
    },
  ],
  notes: [
    {
      id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      createdAt: now,
      author: "Local User",
      body: "Review hybrid expectations before applying.",
    },
  ],
  externalLinks: [{ label: "Job posting", url: "https://example.com/jobs/123", type: "posting" }],
  metadata: {},
  createdAt: now,
  updatedAt: now,
};

export const canonicalExamples = {
  Workspace: workspaceExample,
  Opportunity: opportunityExample,
  StrideEvaluation: strideEvaluationExample,
  ResumeArtifact: resumeArtifactExample,
  CoverLetterArtifact: coverLetterArtifactExample,
  ApplicationState: applicationStateExample,
} as const;
