from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.patient import Patient, NeedRiskLevel
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.ml.inference import prediction_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    blood_group: Optional[str] = None,
    risk: Optional[NeedRiskLevel] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Patient)
    if search:
        query = query.filter((Patient.name.ilike(f"%{search}%")) | (Patient.patient_code.ilike(f"%{search}%")))
    if blood_group:
        query = query.filter(Patient.blood_group == blood_group.strip().upper())
    if risk:
        query = query.filter(Patient.risk_level == risk)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(Patient).filter(Patient.patient_code == patient_in.patient_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient code already exists")
    
    # Run initial ML prediction
    pred = prediction_service.predict_need({
        "hb_level": patient_in.hb_level,
        "recent_hb_drop": patient_in.recent_hb_drop,
        "fatigue_score": patient_in.fatigue_score,
        "prior_delay_count": patient_in.prior_delay_count,
        "infection_flag": patient_in.infection_flag,
        "appointment_adherence": patient_in.appointment_adherence,
        "usual_interval_days": patient_in.transfusion_interval_days
    })

    patient = Patient(
        patient_code=patient_in.patient_code,
        name=patient_in.name,
        date_of_birth=patient_in.date_of_birth,
        blood_group=patient_in.blood_group.upper(),
        city=patient_in.city,
        hospital_name=patient_in.hospital_name,
        hospital_id=patient_in.hospital_id,
        transfusion_interval_days=patient_in.transfusion_interval_days,
        last_transfusion_date=patient_in.last_transfusion_date,
        hb_level=patient_in.hb_level,
        recent_hb_drop=patient_in.recent_hb_drop,
        fatigue_score=patient_in.fatigue_score,
        prior_delay_count=patient_in.prior_delay_count,
        infection_flag=patient_in.infection_flag,
        appointment_adherence=patient_in.appointment_adherence,
        need_probability=pred["need_probability"],
        risk_level=pred["risk_level"]
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/{patient_id}/predictions")
def get_patient_prediction(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    days_since = 18
    if patient.last_transfusion_date:
        days_since = (datetime.now() - patient.last_transfusion_date).days

    pred = prediction_service.predict_need({
        "days_since_transfusion": max(1, days_since),
        "usual_interval_days": patient.transfusion_interval_days,
        "hb_level": patient.hb_level,
        "recent_hb_drop": patient.recent_hb_drop,
        "fatigue_score": patient.fatigue_score,
        "prior_delay_count": patient.prior_delay_count,
        "infection_flag": patient.infection_flag,
        "appointment_adherence": patient.appointment_adherence,
    })
    return {"patient_id": patient_id, "patient_code": patient.patient_code, "name": patient.name, **pred}

@router.get("/{patient_id}/timeline")
def get_patient_timeline(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    timeline = [
        {"date": "2026-08-01", "event": "Transfusion Completed", "location": patient.hospital_name, "units": 1},
        {"date": "2026-08-22", "event": "Transfusion Completed", "location": patient.hospital_name, "units": 1},
        {"date": "2026-09-05", "event": "RATHAM AI Prediction", "details": f"7-day need risk evaluated as {patient.risk_level}"},
        {"date": "2026-09-12", "event": "Donor Preparation Initiated", "details": f"Matching candidate pool reserved for {patient.blood_group}"}
    ]
    return {"patient_id": patient_id, "timeline": timeline}
