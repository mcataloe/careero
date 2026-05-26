from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


class AdvisorPacketIncludeOptions(BaseModel):
    artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    external_link_ids: list[uuid.UUID] = Field(default_factory=list)
    interview_stage_ids: list[uuid.UUID] = Field(default_factory=list)
    reminder_ids: list[uuid.UUID] = Field(default_factory=list)
    advisor_context: str | None = Field(default=None, max_length=4000)


class AdvisorPacketWarning(BaseModel):
    code: str
    message: str


class AdvisorPacketRedaction(BaseModel):
    data_class: str
    field: str | None = None
    default_visibility: str
    status: Literal["included", "excluded", "summary_only"]
    included: bool
    reason: str
    warning: str | None = None


class AdvisorPacketSection(BaseModel):
    key: str
    title: str
    status: Literal["included", "excluded", "summary_only"]
    item_count: int = 0
    warnings: list[AdvisorPacketWarning] = Field(default_factory=list)


class AdvisorPacketOpportunitySummary(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    company_name: str
    status: str
    location: str | None = None
    remote_type: str | None = None


class AdvisorPacketApplicationSummary(BaseModel):
    id: uuid.UUID
    current_state: str
    applied_at: datetime | None = None
    next_action_at: datetime | None = None
    counts: dict[str, int] = Field(default_factory=dict)


class AdvisorPacketArtifactSummary(BaseModel):
    id: uuid.UUID
    artifact_type: str
    title: str
    lifecycle_status: str | None = None
    revision_number: int | None = None
    content_included: bool = False
    content: str | None = None
    updated_at: datetime
    warnings: list[AdvisorPacketWarning] = Field(default_factory=list)


class AdvisorPacketExternalLinkSummary(BaseModel):
    id: uuid.UUID
    label: str
    url: str
    link_type: str | None = None
    warning: str


class AdvisorPacketInterviewSummary(BaseModel):
    id: uuid.UUID
    title: str
    stage_type: str
    status: str
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    notes_included: bool = False
    notes: str | None = None
    preparation_notes: str | None = None
    outcome_notes: str | None = None
    warning: str


class AdvisorPacketReminderSummary(BaseModel):
    id: uuid.UUID
    title: str
    due_at: datetime
    completed_at: datetime | None = None
    notes_included: bool = False
    notes: str | None = None
    warning: str


class AdvisorPacketResponse(BaseModel):
    packet_version: str
    mode: Literal["local_preview"]
    generated_at: datetime
    local_only: bool
    external_sharing_enabled: bool
    advisory_notice: str
    include_options: AdvisorPacketIncludeOptions
    sections: list[AdvisorPacketSection] = Field(default_factory=list)
    opportunity: AdvisorPacketOpportunitySummary
    application: AdvisorPacketApplicationSummary
    artifacts: list[AdvisorPacketArtifactSummary] = Field(default_factory=list)
    selected_external_links: list[AdvisorPacketExternalLinkSummary] = Field(default_factory=list)
    selected_interviews: list[AdvisorPacketInterviewSummary] = Field(default_factory=list)
    selected_reminders: list[AdvisorPacketReminderSummary] = Field(default_factory=list)
    advisor_context: str | None = None
    redactions: list[AdvisorPacketRedaction] = Field(default_factory=list)
    warnings: list[AdvisorPacketWarning] = Field(default_factory=list)
