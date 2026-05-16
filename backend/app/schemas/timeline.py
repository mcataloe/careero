from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TimelineEventResponse(BaseModel):
    id: str
    application_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    occurred_at: datetime
    actor: str
    source_type: str
    source_id: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}
