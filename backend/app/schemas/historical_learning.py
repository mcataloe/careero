import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse


class HistoricalLearningSummary(InsightResponse):
    value: str | int | float | None


class HistoricalLearningResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    summaries: list[HistoricalLearningSummary] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
