export type StrategyConfidenceLevel =
  | "insufficient_data"
  | "weak"
  | "moderate"
  | "high";

export interface StrategyConfidence {
  confidence: StrategyConfidenceLevel;
  basis: string;
  sampleSize: number;
  sourceInputs: Record<string, unknown>;
  knownUncertainty: string[];
  insufficientData: string[];
  userOverrides: Record<string, unknown> | null;
}

export interface StrategySignal {
  id: string;
  category: string;
  label: string;
  message: string;
  basis: string;
  severity: "info" | "caution" | "positive";
  confidence: StrategyConfidence;
  sourceInputs: Record<string, unknown>;
}

export interface StrategyActionCandidate {
  id: string;
  category: string;
  title: string;
  rationale: string;
  basis: string;
  confidence: StrategyConfidence;
  sourceInputs: Record<string, unknown>;
  advisoryOnly: true;
}

export interface StrategyInsufficientDataItem {
  reason: string;
  message: string;
  sourceInputs: Record<string, unknown>;
}

export interface StrategySampleSize {
  opportunities: number;
  applications: number;
  submittedApplications: number;
  responses: number;
  compassEvaluations: number;
  artifactPerformanceRecords: number;
}

export interface SearchTrackStrategySummary {
  contractVersion: "careero.contracts.v1";
  workspaceId: string;
  workspaceName: string;
  generatedAt: string;
  summary: string;
  basis: string;
  confidence: StrategyConfidence;
  sampleSize: StrategySampleSize;
  sourceInputs: Record<string, unknown>;
  knownUncertainty: string[];
  insufficientData: StrategyInsufficientDataItem[];
  signals: StrategySignal[];
  compensationAlignment: {
    summary: string;
    basis: string;
    confidence: StrategyConfidence;
    observations: Array<Record<string, unknown>>;
  };
  skillGapThemes: StrategySignal[];
  roleMarketPositioning: {
    summary: string;
    basis: string;
    confidence: StrategyConfidence;
    themes: string[];
  };
  careerNarrativeThemes: StrategySignal[];
  retrospective: {
    summary: string;
    basis: string;
    confidence: StrategyConfidence;
    notes: string[];
  };
  actionCandidates: StrategyActionCandidate[];
  warnings: string[];
}

export interface CrossTrackStrategyComparison {
  generatedAt: string;
  basis: string;
  confidence: StrategyConfidence;
  tracks: Array<{
    workspaceId: string;
    workspaceName: string;
    summary: string;
    sampleSize: Record<string, unknown>;
    signalCount: number;
    warningCount: number;
  }>;
  signals: StrategySignal[];
  insufficientData: StrategyInsufficientDataItem[];
  warnings: string[];
}

export interface CareerStrategySummary {
  contractVersion: "careero.contracts.v1";
  generatedAt: string;
  summary: string;
  workspaceId: string | null;
  workspaceName: string | null;
  activeTrack: SearchTrackStrategySummary | null;
  tracks: SearchTrackStrategySummary[];
  crossTrackComparison: CrossTrackStrategyComparison | null;
  warnings: string[];
}
