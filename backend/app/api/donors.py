from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.donor import Donor, DonorAvailabilityStatus, DonorBurnoutRiskLevel
from app.schemas.donor import DonorCreate, DonorUpdate, DonorResponse, DonorAvailabilityUpdate
from app.ml.inference import prediction_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/donors", tags=["Donors"])

@router.get("", response_model=List[DonorResponse])
def list_donors(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    blood_group: Optional[str] = None,
    availability: Optional[DonorAvailabilityStatus] = None,
    burnout: Optional[DonorBurnoutRiskLevel] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Donor)
    if search:
        query = query.filter((Donor.name.ilike(f"%{search}%")) | (Donor.donor_code.ilike(f"%{search}%")) | (Donor.city.ilike(f"%{search}%")))
    if blood_group:
        query = query.filter(Donor.blood_group == blood_group.strip().upper())
    if availability:
        query = query.filter(Donor.availability_status == availability)
    if burnout:
        query = query.filter(Donor.burnout_risk_level == burnout)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor(donor_in: DonorCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(Donor).filter(Donor.donor_code == donor_in.donor_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Donor code already exists")
    
    donor = Donor(
        donor_code=donor_in.donor_code,
        name=donor_in.name,
        blood_group=donor_in.blood_group.upper(),
        phone=donor_in.phone,
        city=donor_in.city,
        latitude=donor_in.latitude,
        longitude=donor_in.longitude,
        availability_status=donor_in.availability_status,
        preferred_contact_channel=donor_in.preferred_contact_channel
    )

    # Initial ML reachability and burnout calculation
    pred = prediction_service.predict_donor({
        "days_since_last_contact": donor.days_since_last_contact,
        "contacts_last_30d": donor.contacts_last_30d,
        "response_rate_90d": donor.response_rate_90d,
        "avg_response_hours": donor.avg_response_hours,
        "distance_km": donor.distance_km,
        "availability_rate_90d": donor.availability_rate_90d,
        "weekday_availability": donor.weekday_availability,
        "recent_donation_days": donor.recent_donation_days,
        "opt_in_active": donor.opt_in_active,
        "night_contact_ratio": donor.night_contact_ratio,
        "contacts_last_14d": donor.contacts_last_14d,
        "successful_donations_90d": donor.successful_donations_90d,
        "days_since_last_donation": donor.recent_donation_days,
        "response_rate_30d": donor.response_rate_30d,
        "decline_rate_30d": donor.decline_rate_30d,
        "cooldown_days_observed": donor.cooldown_days_observed,
        "engagement_drop_pct": donor.engagement_drop_pct,
        "voluntary_opt_outs": donor.voluntary_opt_outs
    })

    donor.reachability_probability = pred["reachability_probability"]
    donor.burnout_probability = pred["burnout_probability"]
    donor.burnout_risk_level = pred["burnout_risk_level"]

    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor

@router.get("/{donor_id}", response_model=DonorResponse)
def get_donor(donor_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor

@router.patch("/{donor_id}/availability", response_model=DonorResponse)
def update_availability(donor_id: int, update_in: DonorAvailabilityUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.availability_status = update_in.availability_status
    db.commit()
    db.refresh(donor)
    return donor

@router.get("/{donor_id}/risk")
def get_donor_risk(donor_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    pred = prediction_service.predict_donor({
        "days_since_last_contact": donor.days_since_last_contact,
        "contacts_last_30d": donor.contacts_last_30d,
        "response_rate_90d": donor.response_rate_90d,
        "avg_response_hours": donor.avg_response_hours,
        "distance_km": donor.distance_km,
        "availability_rate_90d": donor.availability_rate_90d,
        "weekday_availability": donor.weekday_availability,
        "recent_donation_days": donor.recent_donation_days,
        "opt_in_active": donor.opt_in_active,
        "night_contact_ratio": donor.night_contact_ratio,
        "contacts_last_14d": donor.contacts_last_14d,
        "successful_donations_90d": donor.successful_donations_90d,
        "days_since_last_donation": donor.recent_donation_days,
        "response_rate_30d": donor.response_rate_30d,
        "decline_rate_30d": donor.decline_rate_30d,
        "cooldown_days_observed": donor.cooldown_days_observed,
        "engagement_drop_pct": donor.engagement_drop_pct,
        "voluntary_opt_outs": donor.voluntary_opt_outs
    })
    return {"donor_id": donor_id, "donor_code": donor.donor_code, "name": donor.name, **pred}
