import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.constants import StrideEvaluationStatus


class StrideEvaluationCreate(BaseModel):
    user_notes: str | None = Field(default=None, max_length=5000)
    user_context: dict[str, Any] = Field(default_factory=dict)


class StrideEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    evaluation_status: StrideEvaluationStatus
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
    raw_evaluation_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
