from datetime import datetime
from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field


ArtifactLifecycleStatusLiteral = Literal["draft", "reviewed", "submitted", "archived"]
ArtifactTypeLiteral = Literal["tailored_resume", "cover_letter"]


class ArtifactDraftCreate(BaseModel):
    workspace_id: uuid.UUID
    role_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    artifact_type: ArtifactTypeLiteral
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    evaluation_id: uuid.UUID | None = None
    source_resume_version_id: uuid.UUID | None = None
    source_artifact_id: uuid.UUID | None = None
    change_summary: str | None = Field(default=None, max_length=5000)


class ArtifactDraftUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    change_summary: str | None = Field(default=None, max_length=5000)


class ArtifactTraceabilityResponse(BaseModel):
    workspace_id: uuid.UUID
    role_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    evaluation_id: uuid.UUID | None = None
    source_resume_version_id: uuid.UUID | None = None
    source_artifact_id: uuid.UUID | None = None
    parent_artifact_id: uuid.UUID | None = None
    generation_warnings: list[str] = Field(default_factory=list)
    export_formats: list[str] = Field(default_factory=list)


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    application_id: uuid.UUID | None = None
    role_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    artifact_type: str
    lifecycle_status: ArtifactLifecycleStatusLiteral
    version_number: int
    title: str
    content: str
    reviewed_at: datetime | None = None
    submitted_at: datetime | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    traceability: ArtifactTraceabilityResponse
    available_transitions: list[ArtifactLifecycleStatusLiteral] = Field(default_factory=list)
    new_version_created: bool = False
    source_submitted_artifact_id: uuid.UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
