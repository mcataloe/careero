import uuid

from pydantic import BaseModel, Field

from app.schemas.insights import InsightResponse


class SearchHealthSignal(InsightResponse):
    signal_type: str
    gentle_guidance: str


class SearchHealthResponse(BaseModel):
    generated_at: str
    workspace_id: uuid.UUID | None = None
    signals: list[SearchHealthSignal] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
