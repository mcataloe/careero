import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse

class CompensationObservation(BaseModel):
    opportunity_id: uuid.UUID
    role_id: uuid.UUID
    title: str
    compensation_min: float | None
    compensation_max: float | None
    midpoint: float | None
    currency: str | None
    employment_type: str | None
    remote_type: str | None
    source_basis: str


class CompensationInsight(InsightResponse):
    pass


class CompensationIntelligenceResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    target_compensation_min: float | None = None
    observations: list[CompensationObservation] = Field(default_factory=list)
    insights: list[CompensationInsight] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
