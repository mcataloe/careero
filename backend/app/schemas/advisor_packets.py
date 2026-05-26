from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


class AdvisorPacketWarning(BaseModel):
    code: str
    message: str


class AdvisorPacketRedaction(BaseModel):
    data_class: str
    default_visibility: str
    status: Literal["included", "excluded", "summary_only"]
    reason: str


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
    updated_at: datetime
    warnings: list[AdvisorPacketWarning] = Field(default_factory=list)


class AdvisorPacketResponse(BaseModel):
    packet_version: str
    mode: Literal["local_preview"]
    generated_at: datetime
    local_only: bool
    external_sharing_enabled: bool
    advisory_notice: str
    opportunity: AdvisorPacketOpportunitySummary
    application: AdvisorPacketApplicationSummary
    artifacts: list[AdvisorPacketArtifactSummary] = Field(default_factory=list)
    redactions: list[AdvisorPacketRedaction] = Field(default_factory=list)
    warnings: list[AdvisorPacketWarning] = Field(default_factory=list)
