import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants import RoleStatus, SourceType


class CompanyLookup(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    website_url: str | None = Field(default=None, max_length=2048)

    @model_validator(mode="after")
    def require_id_or_name(self) -> "CompanyLookup":
        if self.id is None and not self.name:
            raise ValueError("company must include either id or name")
        return self


class SourceLookup(BaseModel):
    id: uuid.UUID | None = None
    source_type: SourceType | None = None

    @model_validator(mode="after")
    def require_id_or_type(self) -> "SourceLookup":
        if self.id is None and self.source_type is None:
            raise ValueError("source must include either id or source_type")
        return self


class RoleBase(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    job_url: str | None = Field(default=None, max_length=2048)
    location: str | None = Field(default=None, max_length=255)
    remote_type: str | None = Field(default=None, max_length=100)
    compensation_min: Decimal | None = None
    compensation_max: Decimal | None = None
    compensation_currency: str | None = Field(default=None, min_length=3, max_length=3)
    raw_description: str | None = None
    normalized_description: str | None = None
    status: RoleStatus | None = None
    date_found: date | None = None
    date_posted: date | None = None

    @model_validator(mode="after")
    def compensation_range_must_be_ordered(self) -> "RoleBase":
        if (
            self.compensation_min is not None
            and self.compensation_max is not None
            and self.compensation_min > self.compensation_max
        ):
            raise ValueError("compensation_min cannot be greater than compensation_max")
        return self

    @model_validator(mode="after")
    def normalize_currency(self) -> "RoleBase":
        if self.compensation_currency is not None:
            self.compensation_currency = self.compensation_currency.upper()
        return self


class RoleCreate(RoleBase):
    workspace_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    company: CompanyLookup
    source: SourceLookup
    status: RoleStatus = RoleStatus.FOUND
    parse_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("parse_metadata")
    @classmethod
    def parse_metadata_must_be_object(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return value or {}


class RoleUpdate(RoleBase):
    company: CompanyLookup | None = None
    source: SourceLookup | None = None

    @model_validator(mode="after")
    def required_role_fields_cannot_be_cleared(self) -> "RoleUpdate":
        for field_name in ("title", "status", "date_found"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    website_url: str | None = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    source_type: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    company_id: uuid.UUID
    source_id: uuid.UUID | None
    job_url: str | None
    location: str | None
    remote_type: str | None
    compensation_min: Decimal | None
    compensation_max: Decimal | None
    compensation_currency: str | None
    raw_description: str | None
    normalized_description: str | None
    parse_metadata: dict[str, Any]
    status: str
    date_found: date
    date_posted: date | None
    created_at: datetime
    updated_at: datetime
    company: CompanyResponse
    source: SourceResponse | None = None


class OpportunityCreate(RoleCreate):
    pass


class OpportunityUpdate(RoleUpdate):
    pass


class OpportunityResponse(RoleResponse):
    pass
