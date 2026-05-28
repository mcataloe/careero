from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.constants import (
    ApplicationInterviewStageType,
    ApplicationInterviewStatus,
    ApplicationWorkflowState,
)

ApplicationNoteType = Literal[
    "general",
    "recruiter",
    "compensation",
    "follow_up",
    "interview",
]


class ApplicationCompanySummary(BaseModel):
    id: uuid.UUID
    name: str
    website_url: str | None = None


class ApplicationWorkspaceSummary(BaseModel):
    id: uuid.UUID
    title: str
    status: str


class ApplicationRoleSummary(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    status: str
    company: ApplicationCompanySummary
    job_url: str | None = None
    location: str | None = None
    remote_type: str | None = None


class ApplicationCompassSummary(BaseModel):
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
    external_links: int = 0
    reminders: int = 0
    interviews: int = 0


class ApplicationListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_id: uuid.UUID
    workspace_id: uuid.UUID
    workspace: ApplicationWorkspaceSummary
    title: str
    company: ApplicationCompanySummary
    current_state: ApplicationWorkflowState
    applied_at: datetime | None = None
    next_action_at: datetime | None = None
    updated_at: datetime
    archived_at: datetime | None = None
    available_next_states: list[ApplicationWorkflowState] = Field(default_factory=list)
    compass: ApplicationCompassSummary | None = None
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


class ApplicationTimelineEventResponse(BaseModel):
    id: str
    application_id: uuid.UUID
    event_type: str
    title: str
    description: str | None = None
    occurred_at: datetime
    actor: str
    source_type: str
    source_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApplicationNoteCreate(BaseModel):
    body: str = Field(min_length=1)
    author: str | None = Field(default=None, max_length=200)
    note_type: ApplicationNoteType = "general"


class ApplicationNoteUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, max_length=200)
    note_type: ApplicationNoteType | None = None


class ApplicationNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    workspace_id: uuid.UUID
    author: str | None = None
    note_type: str
    body: str
    created_at: datetime
    updated_at: datetime


class ApplicationReminderCreate(BaseModel):
    due_at: datetime
    title: str = Field(min_length=1, max_length=255)
    notes: str | None = None


class ApplicationReminderUpdate(BaseModel):
    due_at: datetime | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None
    completed_at: datetime | None = None


class ApplicationReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    workspace_id: uuid.UUID
    due_at: datetime
    title: str
    notes: str | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


def _require_timezone(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        raise ValueError("datetime values must include timezone information")
    return value


class ApplicationInterviewStageCreate(BaseModel):
    stage_type: ApplicationInterviewStageType = ApplicationInterviewStageType.OTHER
    title: str = Field(min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    status: ApplicationInterviewStatus | None = None
    interviewer_names: list[str] = Field(default_factory=list)
    location_or_meeting_link: str | None = Field(default=None, max_length=2048)
    notes: str | None = None
    preparation_notes: str | None = None
    outcome_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    _scheduled_at_timezone = field_validator("scheduled_at")(_require_timezone)
    _completed_at_timezone = field_validator("completed_at")(_require_timezone)


class ApplicationInterviewStageUpdate(BaseModel):
    stage_type: ApplicationInterviewStageType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    status: ApplicationInterviewStatus | None = None
    interviewer_names: list[str] | None = None
    location_or_meeting_link: str | None = Field(default=None, max_length=2048)
    notes: str | None = None
    preparation_notes: str | None = None
    outcome_notes: str | None = None
    metadata: dict[str, Any] | None = None

    _scheduled_at_timezone = field_validator("scheduled_at")(_require_timezone)
    _completed_at_timezone = field_validator("completed_at")(_require_timezone)


class ApplicationInterviewCompleteRequest(BaseModel):
    completed_at: datetime | None = None
    outcome_notes: str | None = None
    status: ApplicationInterviewStatus = ApplicationInterviewStatus.COMPLETED

    _completed_at_timezone = field_validator("completed_at")(_require_timezone)


class ApplicationInterviewCancelRequest(BaseModel):
    outcome_notes: str | None = None
    status: ApplicationInterviewStatus = ApplicationInterviewStatus.CANCELED


class ApplicationInterviewStageResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    workspace_id: uuid.UUID
    stage_type: ApplicationInterviewStageType | str
    title: str
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    status: ApplicationInterviewStatus | str
    interviewer_names: list[str] = Field(default_factory=list)
    location_or_meeting_link: str | None = None
    notes: str | None = None
    preparation_notes: str | None = None
    outcome_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    state_transition_suggestion: ApplicationWorkflowState | None = None
    created_at: datetime
    updated_at: datetime


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


class ApplicationExternalLinkResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    workspace_id: uuid.UUID
    label: str
    url: str
    type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
