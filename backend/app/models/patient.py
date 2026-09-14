import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from app.core.database import Base

class NeedRiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PatientStatus(str, enum.Enum):
    STABLE = "STABLE"
    MONITORED = "MONITORED"
    SCHEDULED = "SCHEDULED"
    URGENT = "URGENT"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(String(20), nullable=True)
    blood_group = Column(String(10), index=True, nullable=False)  # e.g., A+, O-, AB+
    city = Column(String(100), index=True, nullable=False)
    hospital_name = Column(String(255), index=True, nullable=False)
    hospital_id = Column(String(100), index=True, nullable=True)
    transfusion_interval_days = Column(Integer, default=21, nullable=False)
    last_transfusion_date = Column(DateTime, nullable=True)
    next_expected_transfusion = Column(DateTime, nullable=True)
    hb_level = Column(Float, default=8.2, nullable=False)
    recent_hb_drop = Column(Float, default=0.45, nullable=False)
    fatigue_score = Column(Integer, default=5, nullable=False)
    prior_delay_count = Column(Integer, default=0, nullable=False)
    infection_flag = Column(Integer, default=0, nullable=False)
    appointment_adherence = Column(Float, default=0.85, nullable=False)
    status = Column(Enum(PatientStatus), default=PatientStatus.MONITORED, nullable=False)
    risk_level = Column(Enum(NeedRiskLevel), default=NeedRiskLevel.LOW, nullable=False)
    need_probability = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
