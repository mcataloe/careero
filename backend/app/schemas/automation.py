import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.constants import (
    AutomationActionType,
    AutomationApprovalStatus,
    AutomationExecutionStatus,
    AutomationSuggestionStatus,
    AutomationTargetType,
)


class AutomationPreview(BaseModel):
    title: str
    body: str
    content_hash: str
    external_mutation: Literal[False] = False


class AutomationSuggestionResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    target_type: AutomationTargetType | str
    target_id: uuid.UUID
    role_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    artifact_id: uuid.UUID | None = None
    action_type: AutomationActionType | str
    title: str
    summary: str
    reason: str
    basis: str
    confidence: str
    source_inputs: dict[str, Any] = Field(default_factory=dict)
    preview: AutomationPreview
    preview_hash: str
    status: AutomationSuggestionStatus | str
    expires_at: datetime | None = None
    policy_version: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class AutomationSuggestionListResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    target_type: AutomationTargetType | str | None = None
    target_id: uuid.UUID | None = None
    suggestions: list[AutomationSuggestionResponse] = Field(default_factory=list)
    external_actions_enabled: Literal[False] = False


class AutomationDecisionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)
    actor: Literal["user"] = "user"


class AutomationApprovalLogResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    suggestion_id: uuid.UUID
    actor: str
    target_type: AutomationTargetType | str
    target_id: uuid.UUID
    action_type: AutomationActionType | str
    preview: AutomationPreview
    preview_hash: str
    approval_status: AutomationApprovalStatus | str
    dismissal_or_rejection_reason: str | None = None
    execution_status: AutomationExecutionStatus | str
    execution_result: dict[str, Any] = Field(default_factory=dict)
    external_mutation: Literal[False] = False
    policy_version: str
    created_at: datetime
    decided_at: datetime | None = None
    executed_at: datetime | None = None


class AutomationApprovalLogListResponse(BaseModel):
    workspace_id: uuid.UUID | None = None
    logs: list[AutomationApprovalLogResponse] = Field(default_factory=list)


class AutomationPreferencesResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    enabled: bool = True
    suggestion_categories: list[AutomationActionType | str] = Field(default_factory=list)
    follow_up_suggestion_days: int = 7
    artifact_readiness_checks_enabled: bool = True
    communication_drafts_enabled: bool = True
    internal_state_change_suggestions_enabled: bool = True
    future_external_actions_enabled: Literal[False] = False
    quiet_mode: bool = False
    policy_version: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class AutomationPreferencesUpdate(BaseModel):
    enabled: bool | None = None
    suggestion_categories: list[AutomationActionType] | None = None
    follow_up_suggestion_days: int | None = Field(default=None, ge=1, le=90)
    artifact_readiness_checks_enabled: bool | None = None
    communication_drafts_enabled: bool | None = None
    internal_state_change_suggestions_enabled: bool | None = None
    future_external_actions_enabled: Literal[False] | None = None
    quiet_mode: bool | None = None
