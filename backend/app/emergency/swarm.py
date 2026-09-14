from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.models.emergency import EmergencyStatus, EmergencyPriority
from app.notifications.provider import get_notification_provider
from app.core.logging import logger

VALID_TRANSITIONS = {
    EmergencyStatus.CREATED: [EmergencyStatus.SEARCHING, EmergencyStatus.CANCELLED],
    EmergencyStatus.SEARCHING: [EmergencyStatus.PRIMARY_CONTACTED, EmergencyStatus.BACKUP_SEARCH, EmergencyStatus.CANCELLED],
    EmergencyStatus.PRIMARY_CONTACTED: [EmergencyStatus.DONOR_CONFIRMED, EmergencyStatus.PRIMARY_DECLINED, EmergencyStatus.EXPIRED, EmergencyStatus.CANCELLED],
    EmergencyStatus.PRIMARY_DECLINED: [EmergencyStatus.BACKUP_SEARCH, EmergencyStatus.ESCALATED, EmergencyStatus.CANCELLED],
    EmergencyStatus.BACKUP_SEARCH: [EmergencyStatus.BACKUP_CONTACTED, EmergencyStatus.ESCALATED, EmergencyStatus.CANCELLED],
    EmergencyStatus.BACKUP_CONTACTED: [EmergencyStatus.DONOR_CONFIRMED, EmergencyStatus.ESCALATED, EmergencyStatus.CANCELLED, EmergencyStatus.EXPIRED],
    EmergencyStatus.DONOR_CONFIRMED: [EmergencyStatus.FULFILLED, EmergencyStatus.CANCELLED],
    EmergencyStatus.ESCALATED: [EmergencyStatus.DONOR_CONFIRMED, EmergencyStatus.FULFILLED, EmergencyStatus.CANCELLED],
    EmergencyStatus.FULFILLED: [],
    EmergencyStatus.CANCELLED: [],
    EmergencyStatus.EXPIRED: [],
}

class EmergencySwarmEngine:
    def validate_transition(self, current_status: EmergencyStatus, next_status: EmergencyStatus) -> bool:
        allowed = VALID_TRANSITIONS.get(current_status, [])
        return next_status in allowed

    def dispatch_wave(
        self,
        emergency_id: int,
        wave_number: int,
        candidates: List[Dict[str, Any]],
        patient_name: str,
        blood_group: str,
        hospital_name: str
    ) -> Dict[str, Any]:
        provider = get_notification_provider()
        dispatched = []

        message = (
            f"URGENT RATHAM BLOOD REQUEST: {blood_group} required at {hospital_name} "
            f"for Patient {patient_name}. Reply YES to confirm or NO to decline."
        )

        for candidate in candidates:
            phone = candidate.get("phone", "+91 98765 43210")
            res = provider.send_notification(
                donor_phone=phone,
                message=message,
                metadata={"emergency_id": emergency_id, "donor_id": candidate.get("donor_id")}
            )
            dispatched.append({
                "donor_id": candidate.get("donor_id"),
                "donor_code": candidate.get("donor_code"),
                "name": candidate.get("name"),
                "status": res["status"],
                "wave": wave_number
            })

        logger.info(f"[SWARM ENGINE] Dispatched Wave {wave_number} with {len(dispatched)} candidate notifications.")

        return {
            "wave_number": wave_number,
            "dispatched_count": len(dispatched),
            "candidates": dispatched,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

swarm_engine = EmergencySwarmEngine()
