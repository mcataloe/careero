import uuid
from typing import Any

from pydantic import BaseModel, Field


class CompensationObservation(BaseModel):
    role_id: uuid.UUID
    title: str
    compensation_min: float | None
    compensation_max: float | None
    midpoint: float | None
    currency: str | None
    employment_type: str | None
    remote_type: str | None
    source_basis: str


class CompensationInsight(BaseModel):
    label: str
    message: str
    basis: str
    confidence: str
    severity: str = "info"
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class CompensationIntelligenceResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    target_compensation_min: float | None = None
    observations: list[CompensationObservation] = Field(default_factory=list)
    insights: list[CompensationInsight] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
