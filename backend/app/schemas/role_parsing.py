from __future__ import annotations

from datetime import date
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
    compensation_min: float | None = Field(default=None, alias="compensationMin")
    compensation_max: float | None = Field(default=None, alias="compensationMax")
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
        normalized = value.strip().upper()
        if not normalized.isalpha() or len(normalized) != 3:
            return None
        return normalized

    @field_validator("compensation_min", "compensation_max")
    @classmethod
    def compensation_must_be_non_negative(
        cls,
        value: float | None,
    ) -> float | None:
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
        value,
    ):
        if not isinstance(value, dict):
            return value
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


class RoleParseConfidence(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_title: float | None = Field(alias="roleTitle", ge=0, le=1)
    company: float | None = Field(ge=0, le=1)
    company_website: float | None = Field(alias="companyWebsite", ge=0, le=1)
    job_url: float | None = Field(alias="jobUrl", ge=0, le=1)
    source: float | None = Field(ge=0, le=1)
    location: float | None = Field(ge=0, le=1)
    remote_type: float | None = Field(alias="remoteType", ge=0, le=1)
    compensation_min: float | None = Field(alias="compensationMin", ge=0, le=1)
    compensation_max: float | None = Field(alias="compensationMax", ge=0, le=1)
    currency: float | None = Field(ge=0, le=1)
    employment_type: float | None = Field(alias="employmentType", ge=0, le=1)
    seniority: float | None = Field(ge=0, le=1)
    date_posted: float | None = Field(alias="datePosted", ge=0, le=1)
    normalized_description: float | None = Field(alias="normalizedDescription", ge=0, le=1)
    extracted_skills: float | None = Field(alias="extractedSkills", ge=0, le=1)


class RoleParseAIOutput(ParsedRole):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    role_title: str | None = Field(alias="roleTitle", max_length=255)
    company: str | None = Field(max_length=255)
    company_website: str | None = Field(alias="companyWebsite", max_length=2048)
    job_url: str | None = Field(alias="jobUrl", max_length=2048)
    source: SourceType | None
    location: str | None = Field(max_length=255)
    remote_type: RemoteType | None = Field(alias="remoteType")
    compensation_min: float | None = Field(alias="compensationMin")
    compensation_max: float | None = Field(alias="compensationMax")
    currency: str | None = Field(min_length=3, max_length=3)
    employment_type: str | None = Field(alias="employmentType", max_length=100)
    seniority: str | None = Field(max_length=100)
    date_posted: date | None = Field(alias="datePosted")
    normalized_description: str | None = Field(alias="normalizedDescription")
    extracted_skills: list[str] = Field(alias="extractedSkills")
    warnings: list[str]
    confidence: RoleParseConfidence


def _validate_url(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    _url_adapter.validate_python(normalized)
    return normalized
