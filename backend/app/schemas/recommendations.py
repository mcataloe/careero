import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse


class RecommendationResponse(InsightResponse):
    recommendation_type: str
    subject_type: str
    subject_id: uuid.UUID | None = None
    action: str
    title: str
    reason: str


class RecommendationListResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    recommendations: list[RecommendationResponse] = Field(default_factory=list)
    read_only: bool = True
