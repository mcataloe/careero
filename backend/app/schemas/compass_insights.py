import uuid
from typing import Any

from pydantic import BaseModel, Field


class CompassTrendInsight(BaseModel):
    label: str
    message: str
    basis: str
    confidence: str
    severity: str = "info"
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class CompassTrendPoint(BaseModel):
    role_id: uuid.UUID
    created_at: str
    overall_score: float | None
    compensation_midpoint: float | None
    seniority_level: int | None
    role_category: str


class CompassInsightsResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    average_compass_score: float | None = None
    trend_points: list[CompassTrendPoint] = Field(default_factory=list)
    insights: list[CompassTrendInsight] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
