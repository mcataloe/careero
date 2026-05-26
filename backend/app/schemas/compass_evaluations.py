import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.constants import CompassEvaluationStatus


class CompassEvaluationCreate(BaseModel):
    user_notes: str | None = Field(default=None, max_length=5000)
    user_context: dict[str, Any] = Field(default_factory=dict)
    force: bool = False


class CompassEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    role_id: uuid.UUID
    evaluation_status: CompassEvaluationStatus
    overall_score: Decimal | None
    recommendation: str | None
    confidence_level: str | None
    summary: str | None
    strengths: list[dict[str, Any]]
    concerns: list[dict[str, Any]]
    resume_alignment: dict[str, Any]
    compensation_alignment: dict[str, Any]
    seniority_alignment: dict[str, Any]
    remote_alignment: dict[str, Any]
    technical_alignment: dict[str, Any]
    company_risk: dict[str, Any]
    ats_keywords: list[str]
    missing_keywords: list[str]
    model_used: str | None
    prompt_version: str | None
    ruleset_version: str | None
    input_token_estimate: int | None
    output_token_estimate: int | None
    latency_ms: int | None
    ai_enabled: bool
    ai_status: str | None
    error_message: str | None
    role_content_hash: str | None
    source_hash: str | None
    evaluation_input_hash: str | None
    raw_evaluation_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
