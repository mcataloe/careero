import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.constants import WorkspaceStatus, WorkspaceType


class WorkspaceMoney(BaseModel):
    min: float | None = None
    max: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    period: str | None = None
    sourceText: str | None = None


class WorkspacePreferences(BaseModel):
    targetTitles: list[str] = Field(default_factory=list)
    targetSeniority: list[str] = Field(default_factory=list)
    preferredRemoteTypes: list[str] = Field(default_factory=list)
    preferredLocations: list[str] = Field(default_factory=list)
    targetCompensation: WorkspaceMoney | None = None
    targetKeywords: list[str] = Field(default_factory=list)
    avoidKeywords: list[str] = Field(default_factory=list)
    notes: str | None = None


class WorkspaceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    workspace_type: WorkspaceType = WorkspaceType.FULL_TIME_INDIVIDUAL_CONTRIBUTOR
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    preferences: WorkspacePreferences = Field(default_factory=WorkspacePreferences)
    ai_context_summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    workspace_type: WorkspaceType | None = None
    status: WorkspaceStatus | None = None
    preferences: WorkspacePreferences | None = None
    ai_context_summary: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    workspace_type: str
    status: str
    preferences: dict[str, Any]
    ai_context_summary: str | None
    tags: list[str]
    metadata: dict[str, Any]
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
