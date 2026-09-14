from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base

class DonationHistory(Base):
    __tablename__ = "donation_history"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True)
    donation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    blood_group = Column(String(10), nullable=False)
    location = Column(String(255), nullable=False)
    successful = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
