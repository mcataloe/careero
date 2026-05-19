import uuid
from typing import Any

from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    id: str
    recommendation_type: str
    subject_type: str
    subject_id: uuid.UUID | None = None
    action: str
    title: str
    reason: str
    basis: str
    confidence: str
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class RecommendationListResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    recommendations: list[RecommendationResponse] = Field(default_factory=list)
    read_only: bool = True
