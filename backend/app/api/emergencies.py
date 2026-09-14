from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.emergency import EmergencyRequest, EmergencyStatus, EmergencyPriority
from app.models.patient import Patient
from app.models.donor import Donor, DonorAvailabilityStatus
from app.models.audit import AuditEvent
from app.schemas.emergency import EmergencyCreate, EmergencyUpdate, EmergencyResponse
from app.emergency.swarm import swarm_engine
from app.matching.engine import matching_engine
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/emergencies", tags=["Emergency Operations"])

@router.get("", response_model=List[EmergencyResponse])
def list_emergencies(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[EmergencyStatus] = None,
    priority: Optional[EmergencyPriority] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(EmergencyRequest)
    if status_filter:
        query = query.filter(EmergencyRequest.status == status_filter)
    if priority:
        query = query.filter(EmergencyRequest.priority == priority)
    emergencies = query.order_by(EmergencyRequest.created_at.desc()).offset(skip).limit(limit).all()

    donors = db.query(Donor).filter(Donor.availability_status != DonorAvailabilityStatus.UNAVAILABLE).all()
    donors_data = [{
        "id": d.id, "donor_code": d.donor_code, "name": d.name, "blood_group": d.blood_group,
        "phone": d.phone, "availability_status": d.availability_status.value, "distance_km": d.distance_km,
        "response_rate_90d": d.response_rate_90d, "availability_rate_90d": d.availability_rate_90d,
        "contacts_last_14d": d.contacts_last_14d, "contacts_last_30d": d.contacts_last_30d,
        "successful_donations_90d": d.successful_donations_90d, "days_since_last_donation": d.recent_donation_days,
        "response_rate_30d": d.response_rate_30d, "decline_rate_30d": d.decline_rate_30d,
        "cooldown_days_observed": d.cooldown_days_observed, "engagement_drop_pct": d.engagement_drop_pct,
        "avg_response_hours": d.avg_response_hours, "voluntary_opt_outs": d.voluntary_opt_outs,
        "opt_in_active": d.opt_in_active, "night_contact_ratio": d.night_contact_ratio,
        "recent_donation_days": d.recent_donation_days, "weekday_availability": d.weekday_availability
    } for d in donors]

    result = []
    for em in emergencies:
        ranked = matching_engine.rank_donors(em.blood_group, donors_data)
        item = EmergencyResponse.model_validate(em).model_dump()
        item["ranked_candidates"] = ranked[:5]
        result.append(item)
    return result

@router.post("", response_model=EmergencyResponse, status_code=status.HTTP_201_CREATED)
def create_emergency(req_in: EmergencyCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == req_in.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    code = f"RTH-{int(datetime.now().timestamp()) % 100000:05d}"
    
    emergency = EmergencyRequest(
        request_code=code,
        patient_id=patient.id,
        blood_group=req_in.blood_group.upper(),
        units_required=req_in.units_required,
        hospital_name=req_in.hospital_name,
        priority=req_in.priority,
        status=EmergencyStatus.CREATED,
        current_wave=1,
        notes=req_in.notes
    )
    db.add(emergency)

    audit = AuditEvent(
        actor_id=str(current_user.name),
        action="EMERGENCY_CREATED",
        entity_type="EMERGENCY",
        entity_id=code,
        details={"patient": patient.name, "blood_group": emergency.blood_group}
    )
    db.add(audit)
    db.commit()
    db.refresh(emergency)

    # Immediately activate searching and donor matching
    activate_emergency(emergency.id, db, current_user)
    db.refresh(emergency)

    return emergency

@router.get("/{emergency_id}", response_model=EmergencyResponse)
def get_emergency(emergency_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency request not found")
    
    # Calculate live candidate donor ranks for dashboard display
    donors = db.query(Donor).filter(Donor.availability_status != DonorAvailabilityStatus.UNAVAILABLE).all()
    donors_data = [{
        "id": d.id, "donor_code": d.donor_code, "name": d.name, "blood_group": d.blood_group,
        "phone": d.phone, "availability_status": d.availability_status.value, "distance_km": d.distance_km,
        "response_rate_90d": d.response_rate_90d, "availability_rate_90d": d.availability_rate_90d,
        "contacts_last_14d": d.contacts_last_14d, "contacts_last_30d": d.contacts_last_30d,
        "successful_donations_90d": d.successful_donations_90d, "days_since_last_donation": d.recent_donation_days,
        "response_rate_30d": d.response_rate_30d, "decline_rate_30d": d.decline_rate_30d,
        "cooldown_days_observed": d.cooldown_days_observed, "engagement_drop_pct": d.engagement_drop_pct,
        "avg_response_hours": d.avg_response_hours, "voluntary_opt_outs": d.voluntary_opt_outs,
        "opt_in_active": d.opt_in_active, "night_contact_ratio": d.night_contact_ratio,
        "recent_donation_days": d.recent_donation_days, "weekday_availability": d.weekday_availability
    } for d in donors]

    ranked = matching_engine.rank_donors(emergency.blood_group, donors_data)
    
    res_dict = EmergencyResponse.model_validate(emergency).model_dump()
    res_dict["ranked_candidates"] = ranked[:5]
    return res_dict

@router.post("/{emergency_id}/activate")
def activate_emergency(emergency_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency request not found")

    patient = db.query(Patient).filter(Patient.id == emergency.patient_id).first()

    emergency.status = EmergencyStatus.PRIMARY_CONTACTED
    emergency.current_wave = 1
    
    # Get candidates
    donors = db.query(Donor).filter(Donor.availability_status == DonorAvailabilityStatus.AVAILABLE).all()
    donors_data = [{"id": d.id, "donor_code": d.donor_code, "name": d.name, "blood_group": d.blood_group, "phone": d.phone, "distance_km": d.distance_km, "response_rate_90d": d.response_rate_90d, "availability_rate_90d": d.availability_rate_90d, "contacts_last_14d": d.contacts_last_14d, "contacts_last_30d": d.contacts_last_30d, "successful_donations_90d": d.successful_donations_90d, "days_since_last_donation": d.recent_donation_days, "response_rate_30d": d.response_rate_30d, "decline_rate_30d": d.decline_rate_30d, "cooldown_days_observed": d.cooldown_days_observed, "engagement_drop_pct": d.engagement_drop_pct, "avg_response_hours": d.avg_response_hours, "voluntary_opt_outs": d.voluntary_opt_outs, "opt_in_active": d.opt_in_active, "night_contact_ratio": d.night_contact_ratio, "recent_donation_days": d.recent_donation_days, "weekday_availability": d.weekday_availability} for d in donors]

    ranked = matching_engine.rank_donors(emergency.blood_group, donors_data)

    if ranked:
        emergency.primary_donor_id = ranked[0]["donor_id"]
        swarm_engine.dispatch_wave(
            emergency_id=emergency.id,
            wave_number=1,
            candidates=[ranked[0]],
            patient_name=patient.name if patient else "Emergency Patient",
            blood_group=emergency.blood_group,
            hospital_name=emergency.hospital_name
        )

    db.add(AuditEvent(
        actor_id=str(current_user.name),
        action="PRIMARY_DONOR_CONTACTED",
        entity_type="EMERGENCY",
        entity_id=emergency.request_code,
        details={"primary_donor_id": emergency.primary_donor_id}
    ))
    db.commit()
    return {"status": "success", "emergency_status": emergency.status.value}

@router.post("/{emergency_id}/decline")
def primary_decline_swarm(emergency_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency request not found")

    patient = db.query(Patient).filter(Patient.id == emergency.patient_id).first()

    emergency.status = EmergencyStatus.BACKUP_CONTACTED
    emergency.current_wave = 2

    # Exclude primary donor, rank remaining backup wave candidates
    donors = db.query(Donor).filter(Donor.availability_status == DonorAvailabilityStatus.AVAILABLE).all()
    donors_data = [{"id": d.id, "donor_code": d.donor_code, "name": d.name, "blood_group": d.blood_group, "phone": d.phone, "distance_km": d.distance_km, "response_rate_90d": d.response_rate_90d, "availability_rate_90d": d.availability_rate_90d, "contacts_last_14d": d.contacts_last_14d, "contacts_last_30d": d.contacts_last_30d, "successful_donations_90d": d.successful_donations_90d, "days_since_last_donation": d.recent_donation_days, "response_rate_30d": d.response_rate_30d, "decline_rate_30d": d.decline_rate_30d, "cooldown_days_observed": d.cooldown_days_observed, "engagement_drop_pct": d.engagement_drop_pct, "avg_response_hours": d.avg_response_hours, "voluntary_opt_outs": d.voluntary_opt_outs, "opt_in_active": d.opt_in_active, "night_contact_ratio": d.night_contact_ratio, "recent_donation_days": d.recent_donation_days, "weekday_availability": d.weekday_availability} for d in donors if d.id != emergency.primary_donor_id]

    ranked = matching_engine.rank_donors(emergency.blood_group, donors_data)

    backups = ranked[:3]
    swarm_engine.dispatch_wave(
        emergency_id=emergency.id,
        wave_number=2,
        candidates=backups,
        patient_name=patient.name if patient else "Emergency Patient",
        blood_group=emergency.blood_group,
        hospital_name=emergency.hospital_name
    )

    db.add(AuditEvent(
        actor_id=str(current_user.name),
        action="PRIMARY_DONOR_DECLINED_SWARM_ACTIVATED",
        entity_type="EMERGENCY",
        entity_id=emergency.request_code,
        details={"wave": 2, "backups_contacted": len(backups)}
    ))
    db.commit()
    return {"status": "success", "emergency_status": emergency.status.value, "wave": 2, "backups_notified": len(backups)}

@router.post("/{emergency_id}/confirm")
def confirm_emergency(emergency_id: int, donor_id: Optional[int] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency request not found")

    confirmed_id = donor_id or emergency.primary_donor_id
    emergency.confirmed_donor_id = confirmed_id
    emergency.status = EmergencyStatus.FULFILLED
    emergency.resolved_at = datetime.now(timezone.utc)

    db.add(AuditEvent(
        actor_id=str(current_user.name),
        action="EMERGENCY_FULFILLED",
        entity_type="EMERGENCY",
        entity_id=emergency.request_code,
        details={"confirmed_donor_id": confirmed_id}
    ))
    db.commit()
    return {"status": "success", "emergency_status": emergency.status.value, "confirmed_donor_id": confirmed_id}
