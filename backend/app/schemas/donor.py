from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.donor import DonorAvailabilityStatus, DonorBurnoutRiskLevel

class DonorInputSchema(BaseModel):
    days_since_last_contact: int = Field(ge=0, le=90, default=5)
    contacts_last_30d: int = Field(ge=0, le=60, default=2)
    contacts_last_14d: int = Field(ge=0, le=60, default=1)
    response_rate_90d: float = Field(ge=0.0, le=1.0, default=0.85)
    response_rate_30d: float = Field(ge=0.0, le=1.0, default=0.80)
    decline_rate_30d: float = Field(ge=0.0, le=1.0, default=0.15)
    avg_response_hours: float = Field(ge=0.1, le=100.0, default=1.5)
    distance_km: float = Field(ge=0.0, le=500.0, default=5.0)
    availability_rate_90d: float = Field(ge=0.0, le=1.0, default=0.85)
    weekday_availability: float = Field(ge=0.0, le=1.0, default=0.80)
    recent_donation_days: int = Field(ge=0, le=1000, default=90)
    opt_in_active: int = Field(ge=0, le=1, default=1)
    night_contact_ratio: float = Field(ge=0.0, le=1.0, default=0.1)
    successful_donations_90d: int = Field(ge=0, le=30, default=1)
    cooldown_days_observed: int = Field(ge=0, le=90, default=10)
    engagement_drop_pct: float = Field(ge=0.0, le=100.0, default=5.0)
    voluntary_opt_outs: int = Field(ge=0, le=20, default=0)

class DonorCreate(BaseModel):
    donor_code: str
    name: str
    blood_group: str
    phone: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None
    donation_count: int = 0
    availability_status: DonorAvailabilityStatus = DonorAvailabilityStatus.AVAILABLE
    preferred_contact_channel: str = "WHATSAPP"

class DonorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    availability_status: Optional[DonorAvailabilityStatus] = None
    cooldown_until: Optional[datetime] = None

class DonorAvailabilityUpdate(BaseModel):
    availability_status: DonorAvailabilityStatus

class DonorResponse(BaseModel):
    id: int
    donor_code: str
    name: str
    blood_group: str
    phone: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None
    donation_count: int
    availability_status: DonorAvailabilityStatus
    preferred_contact_channel: str
    consent_status: bool
    cooldown_until: Optional[datetime] = None
    reachability_probability: float
    burnout_probability: float
    burnout_risk_level: DonorBurnoutRiskLevel
    days_since_last_contact: int
    contacts_last_30d: int
    response_rate_90d: float
    avg_response_hours: float
    distance_km: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
