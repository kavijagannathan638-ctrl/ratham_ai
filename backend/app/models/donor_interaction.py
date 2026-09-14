from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from app.core.database import Base

class DonorInteraction(Base):
    __tablename__ = "donor_interactions"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    emergency_request_id = Column(Integer, nullable=True, index=True)
    contacted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    channel = Column(String(50), default="WHATSAPP", nullable=False)
    response = Column(String(50), nullable=True)  # ACCEPTED, DECLINED, NO_RESPONSE, TIMEOUT
    response_time_seconds = Column(Float, nullable=True)
    accepted = Column(Boolean, default=False, nullable=False)
    declined = Column(Boolean, default=False, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
