import uuid
from typing import Any

from pydantic import BaseModel, Field


class HistoricalLearningSummary(BaseModel):
    label: str
    value: str | int | float | None
    basis: str
    confidence: str
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class HistoricalLearningResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    summaries: list[HistoricalLearningSummary] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
