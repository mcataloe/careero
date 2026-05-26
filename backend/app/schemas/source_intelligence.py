import uuid
from typing import Any

from pydantic import BaseModel, Field


class SourceSummaryMetric(BaseModel):
    source_type: str
    label: str
    opportunities: int
    applications: int
    responses: int
    interviews: int
    response_rate: float | None
    interview_rate: float | None
    average_compass_score: float | None
    recruiter_contacts: int
    compensation_aligned: int
    basis: str


class SourceIntelligenceResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    summaries: list[SourceSummaryMetric] = Field(default_factory=list)
    insights: list[dict[str, Any]] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
