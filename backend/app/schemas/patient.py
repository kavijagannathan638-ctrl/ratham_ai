from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.patient import NeedRiskLevel, PatientStatus

class NeedInputSchema(BaseModel):
    days_since_transfusion: int = Field(ge=0, le=60, default=18)
    usual_interval_days: int = Field(ge=7, le=60, default=21)
    hb_level: float = Field(ge=3.0, le=20.0, default=7.8)
    recent_hb_drop: float = Field(ge=0.0, le=5.0, default=0.6)
    fatigue_score: int = Field(ge=1, le=10, default=6)
    prior_delay_count: int = Field(ge=0, le=20, default=1)
    infection_flag: int = Field(ge=0, le=1, default=0)
    appointment_adherence: float = Field(ge=0.0, le=1.0, default=0.85)

class PatientCreate(BaseModel):
    patient_code: str
    name: str
    date_of_birth: Optional[str] = None
    blood_group: str
    city: str
    hospital_name: str
    hospital_id: Optional[str] = None
    transfusion_interval_days: int = 21
    last_transfusion_date: Optional[datetime] = None
    hb_level: float = 8.2
    recent_hb_drop: float = 0.45
    fatigue_score: int = 5
    prior_delay_count: int = 0
    infection_flag: int = 0
    appointment_adherence: float = 0.85

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    blood_group: Optional[str] = None
    city: Optional[str] = None
    hospital_name: Optional[str] = None
    transfusion_interval_days: Optional[int] = None
    last_transfusion_date: Optional[datetime] = None
    status: Optional[PatientStatus] = None
    hb_level: Optional[float] = None
    recent_hb_drop: Optional[float] = None
    fatigue_score: Optional[int] = None

class PatientResponse(BaseModel):
    id: int
    patient_code: str
    name: str
    date_of_birth: Optional[str] = None
    blood_group: str
    city: str
    hospital_name: str
    hospital_id: Optional[str] = None
    transfusion_interval_days: int
    last_transfusion_date: Optional[datetime] = None
    next_expected_transfusion: Optional[datetime] = None
    hb_level: float
    recent_hb_drop: float
    fatigue_score: int
    prior_delay_count: int
    infection_flag: int
    appointment_adherence: float
    status: PatientStatus
    risk_level: NeedRiskLevel
    need_probability: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
