from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.emergency import EmergencyPriority, EmergencyStatus
from app.schemas.matching import RankedCandidateSchema

class EmergencyCreate(BaseModel):
    patient_id: int
    blood_group: str
    units_required: int = 1
    hospital_name: str
    priority: EmergencyPriority = EmergencyPriority.CRITICAL
    notes: Optional[str] = None

class EmergencyUpdate(BaseModel):
    status: Optional[EmergencyStatus] = None
    priority: Optional[EmergencyPriority] = None
    current_wave: Optional[int] = None
    notes: Optional[str] = None

class EmergencyEventLog(BaseModel):
    timestamp: datetime
    event: str
    actor: str
    details: str

class EmergencyResponse(BaseModel):
    id: int
    request_code: str
    patient_id: int
    blood_group: str
    units_required: int
    hospital_name: str
    priority: EmergencyPriority
    status: EmergencyStatus
    current_wave: int
    primary_donor_id: Optional[int] = None
    confirmed_donor_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    ranked_candidates: List[RankedCandidateSchema] = []

    class Config:
        from_attributes = True
