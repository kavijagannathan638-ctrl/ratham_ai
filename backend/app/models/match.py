from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.core.database import Base

class MatchRecord(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    emergency_request_id = Column(Integer, ForeignKey("emergency_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    match_score = Column(Float, nullable=False)
    reachability_score = Column(Float, nullable=False)
    burnout_score = Column(Float, nullable=False)
    distance_score = Column(Float, nullable=False)
    compatibility_score = Column(Float, nullable=False)
    wave_number = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="RANKED", nullable=False)  # RANKED, CONTACTED, ACCEPTED, DECLINED, TIMEOUT
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
