import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean
from app.core.database import Base

class DonorAvailabilityStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ON_COOLDOWN = "ON_COOLDOWN"
    CONTACTED = "CONTACTED"

class DonorBurnoutRiskLevel(str, enum.Enum):
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    HIGH_RISK = "HIGH_RISK"

class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    donor_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    blood_group = Column(String(10), index=True, nullable=False)
    phone = Column(String(50), nullable=False)
    city = Column(String(100), index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    last_donation_date = Column(DateTime, nullable=True)
    donation_count = Column(Integer, default=0, nullable=False)
    availability_status = Column(Enum(DonorAvailabilityStatus), default=DonorAvailabilityStatus.AVAILABLE, index=True, nullable=False)
    preferred_contact_channel = Column(String(50), default="WHATSAPP", nullable=False)
    consent_status = Column(Boolean, default=True, nullable=False)
    cooldown_until = Column(DateTime, nullable=True)
    
    # ML Feature Columns
    days_since_last_contact = Column(Integer, default=10, nullable=False)
    contacts_last_30d = Column(Integer, default=2, nullable=False)
    contacts_last_14d = Column(Integer, default=1, nullable=False)
    response_rate_90d = Column(Float, default=0.85, nullable=False)
    response_rate_30d = Column(Float, default=0.80, nullable=False)
    decline_rate_30d = Column(Float, default=0.15, nullable=False)
    avg_response_hours = Column(Float, default=1.5, nullable=False)
    distance_km = Column(Float, default=5.0, nullable=False)
    availability_rate_90d = Column(Float, default=0.85, nullable=False)
    weekday_availability = Column(Float, default=0.80, nullable=False)
    recent_donation_days = Column(Integer, default=90, nullable=False)
    opt_in_active = Column(Integer, default=1, nullable=False)
    night_contact_ratio = Column(Float, default=0.1, nullable=False)
    successful_donations_90d = Column(Integer, default=1, nullable=False)
    cooldown_days_observed = Column(Integer, default=10, nullable=False)
    engagement_drop_pct = Column(Float, default=5.0, nullable=False)
    voluntary_opt_outs = Column(Integer, default=0, nullable=False)

    # Derived Model Signals
    reachability_probability = Column(Float, default=0.85, nullable=False)
    burnout_probability = Column(Float, default=0.10, nullable=False)
    burnout_risk_level = Column(Enum(DonorBurnoutRiskLevel), default=DonorBurnoutRiskLevel.HEALTHY, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
