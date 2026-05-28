import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse


class CompassTrendInsight(InsightResponse):
    pass


class CompassTrendPoint(BaseModel):
    role_id: uuid.UUID
    created_at: str
    overall_score: float | None
    compensation_midpoint: float | None
    seniority_level: int | None
    role_category: str


class CompassInsightsResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    average_compass_score: float | None = None
    trend_points: list[CompassTrendPoint] = Field(default_factory=list)
    insights: list[CompassTrendInsight] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
