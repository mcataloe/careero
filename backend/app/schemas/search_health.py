import uuid
from typing import Any

from pydantic import BaseModel, Field


class SearchHealthSignal(BaseModel):
    signal_type: str
    label: str
    message: str
    gentle_guidance: str
    basis: str
    confidence: str
    severity: str = "info"
    source_inputs: dict[str, Any] = Field(default_factory=dict)


class SearchHealthResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    signals: list[SearchHealthSignal] = Field(default_factory=list)
    insufficient_data: list[str] = Field(default_factory=list)
