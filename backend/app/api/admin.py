from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit import AuditEvent
from app.schemas.admin import AuditEventResponse
from app.ml.registry import registry
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Services"])

@router.get("/audits", response_model=List[AuditEventResponse])
def get_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/models")
def get_model_registry_admin(current_user = Depends(get_current_user)):
    return {
        "status": "healthy" if registry.is_healthy() else "degraded",
        "loaded_models": list(registry.models.keys()),
        "metrics": registry.get_metrics()
    }
