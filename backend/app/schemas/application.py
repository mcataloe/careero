from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ChangedByEnum(str, Enum):
    user = "user"
    system = "system"
    automation = "automation"


class ApplicationStateTransitionRequest(BaseModel):
    new_state: str
    reason: Optional[str] = None
    changed_by: ChangedByEnum = ChangedByEnum.user


class ApplicationResponse(BaseModel):
    id: str
    workspace_id: str
    opportunity_id: str
    current_state: str
    available_next_states: List[str]
    # Included for completeness but would expand with real data

    class Config:
        orm_mode = True


class ApplicationPipelineResponse(BaseModel):
    workspace_id: str
    pipeline: dict[str, List[ApplicationResponse]]  # Grouped by state
