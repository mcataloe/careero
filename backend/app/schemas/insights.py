import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


InsightCategory = Literal[
    "fit_alignment",
    "risk_red_flag",
    "compensation",
    "remote_location_alignment",
    "seniority_alignment",
    "application_workflow",
    "artifact_readiness",
    "follow_up_action",
    "cross_opportunity_comparison",
    "search_track_strategy",
    "compass",
    "source_intelligence",
    "historical_learning",
    "other",
    "unknown",
]

InsightGenerationMethod = Literal[
    "ai_generated",
    "deterministic",
    "user_authored",
    "imported",
    "hybrid",
    "unknown",
]

InsightConfidenceLevel = Literal[
    "insufficient_data",
    "weak",
    "moderate",
    "high",
    "unknown",
]

InsightSeverity = Literal["info", "positive", "caution", "warning", "critical"]
InsightVisibility = Literal["internal", "advisor_visible", "user_exportable"]

InsightSourceReferenceType = Literal[
    "opportunity",
    "raw_job_description",
    "parsed_fields",
    "compass_evaluation",
    "resume_source",
    "artifact",
    "user_note",
    "application_event",
    "workspace",
    "other",
]


class InsightScope(BaseModel):
    user_scoped: bool = True
    workspace_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    compass_evaluation_id: uuid.UUID | None = None
    artifact_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None


class InsightSourceReference(BaseModel):
    source_type: InsightSourceReferenceType
    source_id: uuid.UUID | None = None
    label: str
    field: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InsightFreshness(BaseModel):
    generated_at: datetime
    source_updated_at: datetime | None = None
    is_stale: bool = False
    refresh_reason: str | None = None


class InsightRecommendedAction(BaseModel):
    action_type: str
    label: str
    route_path: str | None = None
    review_required: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class InsightResponse(BaseModel):
    id: str
    category: InsightCategory = "other"
    label: str
    message: str
    basis: str
    confidence: str
    confidence_level: InsightConfidenceLevel = "weak"
    confidence_explanation: str | None = None
    known_uncertainty: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    severity: InsightSeverity = "info"
    priority: int | None = None
    generation_method: InsightGenerationMethod = "deterministic"
    visibility: InsightVisibility = "internal"
    scope: InsightScope = Field(default_factory=InsightScope)
    source_references: list[InsightSourceReference] = Field(default_factory=list)
    source_inputs: dict[str, Any] = Field(default_factory=dict)
    freshness: InsightFreshness
    recommended_action: InsightRecommendedAction | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
