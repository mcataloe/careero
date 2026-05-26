from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


AIUsageFeature = Literal[
    "parse_opportunity",
    "compass_enrichment",
    "resume_artifact",
    "cover_letter_artifact",
    "strategy_summary",
    "automation_suggestion",
]

AIUsageEventType = Literal[
    "requested",
    "completed",
    "failed",
    "skipped_disabled",
    "skipped_quota",
    "cache_reused",
]


class AIUsageEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    workspace_id: UUID | None = None
    role_id: UUID | None = None
    application_id: UUID | None = None
    artifact_id: UUID | None = None
    feature: AIUsageFeature
    event_type: AIUsageEventType
    provider: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=100)
    prompt_version: str | None = Field(default=None, max_length=100)
    ruleset_version: str | None = Field(default=None, max_length=100)
    input_token_estimate: int | None = Field(default=None, ge=0)
    output_token_estimate: int | None = Field(default=None, ge=0)
    latency_ms: int | None = Field(default=None, ge=0)
    error_class: str | None = Field(default=None, max_length=200)
    content_hash: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIUsageEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    user_id: UUID
    workspace_id: UUID | None
    role_id: UUID | None
    application_id: UUID | None
    artifact_id: UUID | None
    feature: str
    event_type: str
    provider: str | None
    model: str | None
    status: str
    prompt_version: str | None
    ruleset_version: str | None
    input_token_estimate: int | None
    output_token_estimate: int | None
    latency_ms: int | None
    error_class: str | None
    content_hash: str | None
    metadata: dict[str, Any]
    created_at: datetime


class AIUsageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_events: int
    by_feature: dict[str, int]
    by_event_type: dict[str, int]


class AIUsageListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[AIUsageEventResponse]
    summary: AIUsageSummary
    usage_note: str
