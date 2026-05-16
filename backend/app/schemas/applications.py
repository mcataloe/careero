from datetime import datetime
from decimal import Decimal
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.constants import ApplicationWorkflowState


class ApplicationCompanySummary(BaseModel):
    id: uuid.UUID
    name: str
    website_url: str | None = None


class ApplicationRoleSummary(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    status: str
    company: ApplicationCompanySummary
    job_url: str | None = None
    location: str | None = None
    remote_type: str | None = None


class ApplicationStrideSummary(BaseModel):
    id: uuid.UUID
    evaluation_status: str
    recommendation: str | None = None
    overall_score: Decimal | None = None
    summary: str | None = None
    updated_at: datetime


class ApplicationArtifactSummary(BaseModel):
    id: uuid.UUID
    artifact_type: str
    title: str
    status: str | None = None
    revision_number: int | None = None
    updated_at: datetime


class ApplicationWorkflowCounts(BaseModel):
    notes: int = 0
    reminders: int = 0
    interviews: int = 0


class ApplicationListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    company: ApplicationCompanySummary
    current_state: ApplicationWorkflowState
    applied_at: datetime | None = None
    next_action_at: datetime | None = None
    updated_at: datetime
    archived_at: datetime | None = None
    available_next_states: list[ApplicationWorkflowState] = Field(default_factory=list)
    stride: ApplicationStrideSummary | None = None
    resume_artifact: ApplicationArtifactSummary | None = None
    cover_letter_artifact: ApplicationArtifactSummary | None = None
    counts: ApplicationWorkflowCounts


class ApplicationDetailResponse(ApplicationListItemResponse):
    workflow_metadata: dict[str, Any]
    application_state: dict[str, Any]
    state_history: list[dict[str, Any]]
    role: ApplicationRoleSummary


class ApplicationMetadataUpdate(BaseModel):
    workflow_metadata: dict[str, Any] | None = None
    applied_at: datetime | None = None
    next_action_at: datetime | None = None


class ApplicationStateTransitionRequest(BaseModel):
    state: ApplicationWorkflowState
    reason: str | None = Field(default=None, max_length=5000)
    changed_by: str = Field(default="user", pattern="^(user|system|automation)$")
    metadata: dict[str, Any] = Field(default_factory=dict)
    reactivate: bool = False


class ApplicationPipelineResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    include_inactive: bool = False
    states: dict[str, list[ApplicationListItemResponse]]


class ApplicationNoteCreate(BaseModel):
    body: str = Field(min_length=1)
    author: str | None = Field(default=None, max_length=200)


class ApplicationNoteUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, max_length=200)


class ApplicationReminderCreate(BaseModel):
    due_at: datetime
    title: str = Field(min_length=1, max_length=255)
    notes: str | None = None


class ApplicationReminderUpdate(BaseModel):
    due_at: datetime | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None
    completed_at: datetime | None = None


class ApplicationInterviewStageCreate(BaseModel):
    stage_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApplicationInterviewStageUpdate(BaseModel):
    stage_type: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class ApplicationExternalLinkCreate(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    type: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApplicationExternalLinkUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=255)
    url: HttpUrl | None = None
    type: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] | None = None
