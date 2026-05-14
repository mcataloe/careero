import uuid
from typing import Literal

from pydantic import BaseModel


CoverLetterTone = Literal[
    "direct",
    "warm",
    "executive",
    "technical",
    "consultative",
    "custom",
]


class CoverLetterArtifactGenerateRequest(BaseModel):
    workspace_id: uuid.UUID
    evaluation_id: uuid.UUID | None = None
    source_version_id: uuid.UUID | None = None
    tone: CoverLetterTone = "direct"
