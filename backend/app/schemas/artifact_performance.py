import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse

class ArtifactPerformanceMetric(BaseModel):
    label: str
    artifact_type: str | None = None
    variant_name: str | None = None
    role_category: str | None = None
    total: int
    responses: int
    interviews: int
    response_rate: float | None
    interview_rate: float | None
    basis: str


class ArtifactPerformanceResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    summary: list[ArtifactPerformanceMetric] = Field(default_factory=list)
    by_variant: list[ArtifactPerformanceMetric] = Field(default_factory=list)
    by_role_category: list[ArtifactPerformanceMetric] = Field(default_factory=list)
    insights: list[InsightResponse] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
