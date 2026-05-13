from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

from app.constants import SourceType

_url_adapter = TypeAdapter(AnyUrl)


RemoteType = Literal["remote", "hybrid", "onsite"]


class RoleParseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    raw_text: str = Field(alias="rawText", min_length=1, max_length=100000)
    source: SourceType | None = None
    job_url: str | None = Field(default=None, alias="jobUrl", max_length=2048)

    @field_validator("raw_text")
    @classmethod
    def raw_text_must_have_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("rawText must not be blank")
        return normalized

    @field_validator("job_url")
    @classmethod
    def job_url_must_be_valid(cls, value: str | None) -> str | None:
        return _validate_url(value)


class ParsedRole(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_title: str | None = Field(default=None, alias="roleTitle", max_length=255)
    company: str | None = Field(default=None, max_length=255)
    company_website: str | None = Field(
        default=None,
        alias="companyWebsite",
        max_length=2048,
    )
    job_url: str | None = Field(default=None, alias="jobUrl", max_length=2048)
    source: SourceType | None = None
    location: str | None = Field(default=None, max_length=255)
    remote_type: RemoteType | None = Field(default=None, alias="remoteType")
    compensation_min: Decimal | None = Field(default=None, alias="compensationMin")
    compensation_max: Decimal | None = Field(default=None, alias="compensationMax")
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    employment_type: str | None = Field(
        default=None,
        alias="employmentType",
        max_length=100,
    )
    seniority: str | None = Field(default=None, max_length=100)
    date_posted: date | None = Field(default=None, alias="datePosted")
    normalized_description: str | None = Field(
        default=None,
        alias="normalizedDescription",
    )
    extracted_skills: list[str] = Field(default_factory=list, alias="extractedSkills")
    warnings: list[str] = Field(default_factory=list)
    confidence: dict[str, float] = Field(default_factory=dict)

    @field_validator(
        "role_title",
        "company",
        "location",
        "employment_type",
        "seniority",
        "normalized_description",
        mode="before",
    )
    @classmethod
    def blank_strings_become_null(cls, value):
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @field_validator("remote_type", mode="before")
    @classmethod
    def normalize_remote_type(cls, value):
        if value is None or value == "":
            return None
        normalized = str(value).strip().lower().replace("_", "-")
        if normalized in {"on-site", "on site", "office"}:
            return "onsite"
        return normalized

    @field_validator("company_website", "job_url")
    @classmethod
    def urls_must_be_valid(cls, value: str | None) -> str | None:
        return _validate_url(value)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("compensation_min", "compensation_max")
    @classmethod
    def compensation_must_be_non_negative(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("compensation values must be non-negative")
        return value

    @field_validator("extracted_skills", "warnings")
    @classmethod
    def clean_string_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]

    @field_validator("confidence")
    @classmethod
    def confidence_values_must_be_zero_to_one(
        cls,
        value: dict[str, float],
    ) -> dict[str, float]:
        for field_name, score in value.items():
            if not 0 <= score <= 1:
                raise ValueError(f"confidence for {field_name} must be between 0 and 1")
        return value

    @model_validator(mode="after")
    def compensation_range_must_be_ordered(self) -> "ParsedRole":
        if (
            self.compensation_min is not None
            and self.compensation_max is not None
            and self.compensation_min > self.compensation_max
        ):
            raise ValueError("compensationMin cannot be greater than compensationMax")
        return self


class RoleParseMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    parser_version: str = Field(alias="parserVersion")
    model: str


class RoleParseResponse(BaseModel):
    parsed: ParsedRole
    metadata: RoleParseMetadata


class RoleParseAIOutput(ParsedRole):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def _validate_url(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    _url_adapter.validate_python(normalized)
    return normalized
