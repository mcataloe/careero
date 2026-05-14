import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import ResumeSourceType


class ResumeSourceVersionCreate(BaseModel):
    version_label: str = Field(min_length=1, max_length=100)
    raw_text: str = Field(min_length=1)
    normalized_summary: str | None = None
    is_active: bool = False


class ResumeSourceCreate(ResumeSourceVersionCreate):
    name: str = Field(min_length=1, max_length=255)
    source_type: ResumeSourceType = ResumeSourceType.MASTER_RESUME
    is_active: bool = True


class ResumeSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: ResumeSourceType | None = None


class ResumeSourceVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    version_label: str
    raw_text: str
    normalized_summary: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ResumeSourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    created_at: datetime
    updated_at: datetime
    latest_version: ResumeSourceVersionResponse | None = None
    active_version: ResumeSourceVersionResponse | None = None


class ActiveResumeSourceResponse(BaseModel):
    source: ResumeSourceResponse
    version: ResumeSourceVersionResponse


class ResumeSourceImportResponse(BaseModel):
    file_name: str
    file_type: str
    content_type: str
    size_bytes: int
    character_count: int
    warnings: list[str] = Field(default_factory=list)
    extracted_text: str
