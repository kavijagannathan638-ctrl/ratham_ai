from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.patient import Patient, NeedRiskLevel
from app.models.donor import Donor, DonorAvailabilityStatus, DonorBurnoutRiskLevel
from app.models.emergency import EmergencyRequest, EmergencyStatus
from app.ml.registry import registry
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_overview_analytics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    patients_count = db.query(func.count(Patient.id)).scalar() or 0
    high_risk_patients = db.query(func.count(Patient.id)).filter(Patient.risk_level.in_([NeedRiskLevel.HIGH, NeedRiskLevel.CRITICAL])).scalar() or 0
    donors_count = db.query(func.count(Donor.id)).scalar() or 0
    avail_donors = db.query(func.count(Donor.id)).filter(Donor.availability_status == DonorAvailabilityStatus.AVAILABLE).scalar() or 0
    at_risk_donors = db.query(func.count(Donor.id)).filter(Donor.burnout_risk_level == DonorBurnoutRiskLevel.HIGH_RISK).scalar() or 0
    active_emergencies = db.query(func.count(EmergencyRequest.id)).filter(EmergencyRequest.status.notin_([EmergencyStatus.FULFILLED, EmergencyStatus.CANCELLED])).scalar() or 0
    fulfilled_count = db.query(func.count(EmergencyRequest.id)).filter(EmergencyRequest.status == EmergencyStatus.FULFILLED).scalar() or 0

    demand_trend = [
        {"day": "Mon", "demand": 12, "fulfilled": 11},
        {"day": "Tue", "demand": 15, "fulfilled": 14},
        {"day": "Wed", "demand": 18, "fulfilled": 17},
        {"day": "Thu", "demand": 14, "fulfilled": 14},
        {"day": "Fri", "demand": 21, "fulfilled": 19},
        {"day": "Sat", "demand": 16, "fulfilled": 16},
        {"day": "Sun", "demand": 17, "fulfilled": 16},
    ]

    reach_dist = [
        {"range": "0-25%", "count": db.query(func.count(Donor.id)).filter(Donor.reachability_probability < 0.25).scalar() or 0},
        {"range": "25-50%", "count": db.query(func.count(Donor.id)).filter(Donor.reachability_probability >= 0.25, Donor.reachability_probability < 0.5).scalar() or 0},
        {"range": "50-75%", "count": db.query(func.count(Donor.id)).filter(Donor.reachability_probability >= 0.5, Donor.reachability_probability < 0.75).scalar() or 0},
        {"range": "75-100%", "count": db.query(func.count(Donor.id)).filter(Donor.reachability_probability >= 0.75).scalar() or 0},
    ]

    burn_dist = [
        {"status": "HEALTHY", "count": db.query(func.count(Donor.id)).filter(Donor.burnout_risk_level == DonorBurnoutRiskLevel.HEALTHY).scalar() or 0},
        {"status": "WATCH", "count": db.query(func.count(Donor.id)).filter(Donor.burnout_risk_level == DonorBurnoutRiskLevel.WATCH).scalar() or 0},
        {"status": "HIGH_RISK", "count": at_risk_donors},
    ]

    return {
        "patients_monitored": patients_count,
        "high_risk_patients": high_risk_patients,
        "donors_active": donors_count,
        "available_donors": avail_donors,
        "at_risk_donors": at_risk_donors,
        "active_emergencies": active_emergencies,
        "donor_response_rate": 0.84,
        "requests_fulfilled": fulfilled_count,
        "avg_fulfillment_time_minutes": 14.5,
        "blood_demand_trend": demand_trend,
        "reachability_distribution": reach_dist,
        "burnout_distribution": burn_dist,
        "metrics": registry.get_metrics()
    }

@router.get("/models")
def get_model_analytics(current_user = Depends(get_current_user)):
    return {
        "models_loaded": registry.is_healthy(),
        "metrics": registry.get_metrics()
    }
