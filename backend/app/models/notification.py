import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from app.core.database import Base

class NotificationStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    FAILED = "FAILED"

class NotificationLog(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    emergency_request_id = Column(Integer, nullable=True, index=True)
    channel = Column(String(50), default="WHATSAPP", nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.QUEUED, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
