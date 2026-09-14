from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.emergency import EmergencyRequest, EmergencyStatus
from app.models.audit import AuditEvent
from app.api.emergencies import activate_emergency, primary_decline_swarm, confirm_emergency
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/demo", tags=["Scenario Orchestration Operations"])

@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_demo_scenario(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Safely resets active emergency requests and re-initializes clean operational state.
    """
    db.query(EmergencyRequest).delete()
    db.add(AuditEvent(
        actor_id=str(current_user.name),
        action="SCENARIO_STATE_RESET",
        entity_type="SYSTEM",
        entity_id="ALL",
        details={"message": "Emergency records reset successfully"}
    ))
    db.commit()
    return {"status": "success", "message": "Scenario state reset completed."}

@router.post("/simulate-decline/{emergency_id}")
def simulate_primary_decline(emergency_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return primary_decline_swarm(emergency_id=emergency_id, db=db, current_user=current_user)

@router.post("/simulate-confirm/{emergency_id}")
def simulate_backup_confirm(emergency_id: int, donor_id: int = 2, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return confirm_emergency(emergency_id=emergency_id, donor_id=donor_id, db=db, current_user=current_user)

