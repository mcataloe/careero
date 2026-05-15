from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.constants import ApplicationWorkflowState


class ApplicationStateTransitionRequest(BaseModel):
    state: ApplicationWorkflowState
    reason: str | None = Field(default=None, max_length=5000)
    changed_by: str = Field(default="user", pattern="^(user|system|automation)$")
    metadata: dict[str, Any] = Field(default_factory=dict)


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
