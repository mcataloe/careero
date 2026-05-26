from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


AccountLifecycleRequestType = Literal[
    "data_export",
    "account_deletion",
    "workspace_deletion",
    "source_deletion",
    "artifact_deletion",
    "retention_review",
]

AccountLifecycleStatus = Literal[
    "requested",
    "acknowledged",
    "canceled",
    "completed",
    "rejected",
]


class AccountLifecycleRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_type: AccountLifecycleRequestType
    request_reason: str | None = Field(default=None, max_length=2000)
    target_type: str | None = Field(default=None, max_length=100)
    target_id: UUID | None = None
    request_metadata: dict[str, Any] = Field(default_factory=dict)
    deletion_confirmation: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def deletion_requests_require_confirmation(self) -> "AccountLifecycleRequestCreate":
        if self.request_type == "account_deletion" and (
            self.deletion_confirmation != "record deletion request"
        ):
            raise ValueError(
                "Account deletion requests require deletion_confirmation='record deletion request'"
            )
        return self


class AccountLifecycleRequestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    user_id: UUID
    request_type: str
    status: str
    requested_at: datetime
    acknowledged_at: datetime | None
    completed_at: datetime | None
    canceled_at: datetime | None
    request_reason: str | None
    target_type: str | None
    target_id: UUID | None
    request_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    message: str


class AccountLifecycleRequestListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requests: list[AccountLifecycleRequestResponse]
    lifecycle_note: str
