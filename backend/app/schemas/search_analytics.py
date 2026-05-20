from typing import Any
import uuid

from pydantic import BaseModel, Field


class AnalyticsMetric(BaseModel):
    value: int | float | None
    label: str
    basis: str


class AnalyticsRate(BaseModel):
    numerator: int
    denominator: int
    rate: float | None
    label: str
    basis: str


class StageConversionMetric(BaseModel):
    from_stage: str
    to_stage: str
    numerator: int
    denominator: int
    rate: float | None
    basis: str


class StageDurationMetric(BaseModel):
    from_stage: str
    to_stage: str
    average_days: float | None
    sample_size: int
    basis: str


class SegmentResponseMetric(BaseModel):
    segment: str
    responses: int
    total: int
    response_rate: float | None
    basis: str


class SearchAnalyticsResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    scope: str = "all_workspaces"
    summary: dict[str, AnalyticsMetric]
    conversion_rates: list[StageConversionMetric] = Field(default_factory=list)
    average_stage_durations: list[StageDurationMetric] = Field(default_factory=list)
    segment_response_rates: list[SegmentResponseMetric] = Field(default_factory=list)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
