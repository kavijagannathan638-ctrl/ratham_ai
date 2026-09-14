from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.patient import Patient
from app.models.donor import Donor, DonorAvailabilityStatus
from app.schemas.matching import MatchRequestSchema, MatchResponseSchema, RankedCandidateSchema
from app.matching.engine import matching_engine
from app.ml.inference import prediction_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/matching", tags=["Donor Matching"])

@router.post("/rank", response_model=MatchResponseSchema)
def rank_candidates(req: MatchRequestSchema, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Retrieve or construct patient input
    recipient_blood_group = "O+"
    patient_need_pred = {}

    if req.patient_id:
        patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        recipient_blood_group = patient.blood_group
        patient_need_pred = prediction_service.predict_need({
            "hb_level": patient.hb_level,
            "recent_hb_drop": patient.recent_hb_drop,
            "fatigue_score": patient.fatigue_score,
            "prior_delay_count": patient.prior_delay_count,
            "infection_flag": patient.infection_flag,
            "appointment_adherence": patient.appointment_adherence,
            "usual_interval_days": patient.transfusion_interval_days
        })
    elif req.patient_input:
        recipient_blood_group = "O+"
        patient_need_pred = prediction_service.predict_need(req.patient_input.model_dump())
    else:
        patient_need_pred = prediction_service.predict_need({})

    # Gather donor pool
    donors_data = []
    if req.custom_donors:
        for i, cd in enumerate(req.custom_donors):
            d_dict = cd.model_dump()
            d_dict.update({"id": i + 1, "donor_code": f"DNR-C{i+1}", "name": f"Candidate Donor #{i+1}", "blood_group": recipient_blood_group})
            donors_data.append(d_dict)
    else:
        db_donors = db.query(Donor).filter(Donor.availability_status != DonorAvailabilityStatus.UNAVAILABLE).all()
        for d in db_donors:
            donors_data.append({
                "id": d.id,
                "donor_code": d.donor_code,
                "name": d.name,
                "blood_group": d.blood_group,
                "phone": d.phone,
                "availability_status": d.availability_status.value,
                "distance_km": d.distance_km,
                "response_rate_90d": d.response_rate_90d,
                "availability_rate_90d": d.availability_rate_90d,
                "contacts_last_14d": d.contacts_last_14d,
                "contacts_last_30d": d.contacts_last_30d,
                "successful_donations_90d": d.successful_donations_90d,
                "days_since_last_donation": d.recent_donation_days,
                "response_rate_30d": d.response_rate_30d,
                "decline_rate_30d": d.decline_rate_30d,
                "cooldown_days_observed": d.cooldown_days_observed,
                "engagement_drop_pct": d.engagement_drop_pct,
                "avg_response_hours": d.avg_response_hours,
                "voluntary_opt_outs": d.voluntary_opt_outs,
                "opt_in_active": d.opt_in_active,
                "night_contact_ratio": d.night_contact_ratio,
                "recent_donation_days": d.recent_donation_days,
                "weekday_availability": d.weekday_availability
            })

    ranked = matching_engine.rank_donors(
        recipient_blood_group=recipient_blood_group,
        donors=donors_data,
        patient_need_pred=patient_need_pred
    )

    primary = ranked[0] if ranked else None
    backups = ranked[1:5] if len(ranked) > 1 else []

    return MatchResponseSchema(
        need_prediction=patient_need_pred,
        primary_candidate=primary,
        backup_candidates=backups
    )
