import uuid
from typing import Any

from pydantic import BaseModel, Field


class ResumeArtifactGenerateRequest(BaseModel):
    workspace_id: uuid.UUID
    evaluation_id: uuid.UUID | None = None
    source_version_id: uuid.UUID | None = None


class ResumeArtifactResponse(BaseModel):
    artifact: dict[str, Any] = Field(description="Canonical ResumeArtifact contract")
