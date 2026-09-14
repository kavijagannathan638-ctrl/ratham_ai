from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.core.database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # PATIENT, DONOR
    entity_id = Column(Integer, nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    prediction = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    explanation = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
