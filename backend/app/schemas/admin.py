from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class AuditEventResponse(BaseModel):
    id: int
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
