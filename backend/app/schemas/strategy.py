from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class StrategyModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


StrategyInsufficientDataReason = Literal[
    "empty_workspace",
    "few_opportunities",
    "few_applications",
    "few_outcomes",
    "missing_compass_evaluations",
    "missing_compensation_ranges",
    "missing_artifact_performance",
    "missing_source_history",
    "stale_track",
    "unknown",
]


class StrategyConfidence(StrategyModel):
    confidence: Literal["insufficient_data", "weak", "moderate", "high"]
    basis: str
    sample_size: int
    source_inputs: dict[str, Any] = Field(default_factory=dict)
    known_uncertainty: list[str] = Field(default_factory=list)
    insufficient_data: list[StrategyInsufficientDataReason] = Field(
        default_factory=list
    )
    user_overrides: dict[str, Any] | None = None


class StrategyInsufficientDataItem(StrategyModel):
    reason: StrategyInsufficientDataReason
    message: str
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class StrategySignal(StrategyModel):
    id: str
    category: Literal[
        "search_health",
        "compass",
        "compensation",
        "source",
        "artifact",
        "historical",
        "workspace",
    ]
    label: str
    message: str
    basis: str
    severity: Literal["info", "caution", "positive"] = "info"
    confidence: StrategyConfidence
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class StrategyActionCandidate(StrategyModel):
    id: str
    category: Literal[
        "review_workspace_targets",
        "review_compensation_target",
        "review_skill_gap_plan",
        "review_artifact_strategy",
        "review_source_strategy",
        "archive_or_pause_track_review",
        "create_followup_plan_preview",
        "review_search_focus",
    ]
    title: str
    rationale: str
    basis: str
    confidence: StrategyConfidence
    source_inputs: dict[str, Any] = Field(default_factory=dict)
    advisory_only: Literal[True] = True


class StrategySampleSize(StrategyModel):
    opportunities: int = 0
    applications: int = 0
    submitted_applications: int = 0
    responses: int = 0
    compass_evaluations: int = 0
    artifact_performance_records: int = 0


class CompensationAlignmentSummary(StrategyModel):
    summary: str
    basis: str
    confidence: StrategyConfidence
    observations: list[dict[str, Any]] = Field(default_factory=list)


class RoleMarketPositioningSummary(StrategyModel):
    summary: str
    basis: str
    confidence: StrategyConfidence
    themes: list[str] = Field(default_factory=list)


class StrategyRetrospective(StrategyModel):
    summary: str
    basis: str
    confidence: StrategyConfidence
    notes: list[str] = Field(default_factory=list)


class SearchTrackStrategySummary(StrategyModel):
    contract_version: Literal["careero.contracts.v1"] = "careero.contracts.v1"
    workspace_id: uuid.UUID
    workspace_name: str
    generated_at: datetime
    summary: str
    basis: str
    confidence: StrategyConfidence
    sample_size: StrategySampleSize
    source_inputs: dict[str, Any] = Field(default_factory=dict)
    known_uncertainty: list[str] = Field(default_factory=list)
    insufficient_data: list[StrategyInsufficientDataItem] = Field(
        default_factory=list
    )
    signals: list[StrategySignal] = Field(default_factory=list)
    compensation_alignment: CompensationAlignmentSummary
    skill_gap_themes: list[StrategySignal] = Field(default_factory=list)
    role_market_positioning: RoleMarketPositioningSummary
    career_narrative_themes: list[StrategySignal] = Field(default_factory=list)
    retrospective: StrategyRetrospective
    action_candidates: list[StrategyActionCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CrossTrackStrategyTrack(StrategyModel):
    workspace_id: uuid.UUID
    workspace_name: str
    summary: str
    sample_size: dict[str, Any] = Field(default_factory=dict)
    signal_count: int
    warning_count: int


class CrossTrackStrategyComparison(StrategyModel):
    generated_at: datetime
    basis: str
    confidence: StrategyConfidence
    tracks: list[CrossTrackStrategyTrack] = Field(default_factory=list)
    signals: list[StrategySignal] = Field(default_factory=list)
    insufficient_data: list[StrategyInsufficientDataItem] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)


class CareerStrategySummary(StrategyModel):
    contract_version: Literal["careero.contracts.v1"] = "careero.contracts.v1"
    generated_at: datetime
    summary: str
    workspace_id: uuid.UUID | None = None
    workspace_name: str | None = None
    active_track: SearchTrackStrategySummary | None = None
    tracks: list[SearchTrackStrategySummary] = Field(default_factory=list)
    cross_track_comparison: CrossTrackStrategyComparison | None = None
    warnings: list[str] = Field(default_factory=list)
