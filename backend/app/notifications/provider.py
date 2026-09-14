from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.logging import logger

class BaseNotificationProvider(ABC):
    @abstractmethod
    def send_notification(self, donor_phone: str, message: str, metadata: dict) -> Dict[str, Any]:
        pass

class MockNotificationProvider(BaseNotificationProvider):
    def send_notification(self, donor_phone: str, message: str, metadata: dict) -> Dict[str, Any]:
        logger.info(f"[MOCK NOTIFICATION] Dispatched to {donor_phone}: {message[:60]}...")
        return {
            "status": "SENT",
            "provider": "MOCK",
            "message_id": f"mock_msg_{metadata.get('emergency_id', 1)}_{metadata.get('donor_id', 1)}",
            "delivered": True
        }

class WhatsAppNotificationProvider(BaseNotificationProvider):
    def send_notification(self, donor_phone: str, message: str, metadata: dict) -> Dict[str, Any]:
        logger.info(f"[WHATSAPP] API request to {donor_phone}")
        return {"status": "SENT", "provider": "WHATSAPP", "delivered": True}

class SMSNotificationProvider(BaseNotificationProvider):
    def send_notification(self, donor_phone: str, message: str, metadata: dict) -> Dict[str, Any]:
        logger.info(f"[SMS] Twilio request to {donor_phone}")
        return {"status": "SENT", "provider": "TWILIO_SMS", "delivered": True}

def get_notification_provider() -> BaseNotificationProvider:
    return MockNotificationProvider()
