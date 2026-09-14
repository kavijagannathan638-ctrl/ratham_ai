import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from app.core.database import Base

class EmergencyPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EmergencyStatus(str, enum.Enum):
    CREATED = "CREATED"
    SEARCHING = "SEARCHING"
    PRIMARY_CONTACTED = "PRIMARY_CONTACTED"
    PRIMARY_DECLINED = "PRIMARY_DECLINED"
    BACKUP_SEARCH = "BACKUP_SEARCH"
    BACKUP_CONTACTED = "BACKUP_CONTACTED"
    DONOR_CONFIRMED = "DONOR_CONFIRMED"
    ESCALATED = "ESCALATED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    blood_group = Column(String(10), index=True, nullable=False)
    units_required = Column(Integer, default=1, nullable=False)
    hospital_name = Column(String(255), nullable=False)
    hospital_id = Column(String(100), nullable=True)
    priority = Column(Enum(EmergencyPriority), default=EmergencyPriority.CRITICAL, nullable=False)
    status = Column(Enum(EmergencyStatus), default=EmergencyStatus.CREATED, index=True, nullable=False)
    current_wave = Column(Integer, default=1, nullable=False)
    primary_donor_id = Column(Integer, ForeignKey("donors.id", ondelete="SET NULL"), nullable=True)
    confirmed_donor_id = Column(Integer, ForeignKey("donors.id", ondelete="SET NULL"), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
