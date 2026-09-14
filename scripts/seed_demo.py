from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.patient import Patient, NeedRiskLevel, PatientStatus
from app.models.donor import Donor, DonorAvailabilityStatus, DonorBurnoutRiskLevel
from app.models.donation import DonationHistory
from app.models.emergency import EmergencyRequest, EmergencyPriority, EmergencyStatus
from app.models.audit import AuditEvent
from app.core.security import get_password_hash
from app.ml.inference import prediction_service

def seed_demo_data():
    print("Initializing RATHAM AI operational database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Default Users
        admin_user = User(
            email="admin@ratham.ai",
            name="Super Admin",
            password_hash=get_password_hash("admin123"),
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        coord_user = User(
            email="coordinator@ratham.ai",
            name="City Coordinator",
            password_hash=get_password_hash("coord123"),
            role=UserRole.COORDINATOR,
            is_active=True
        )
        demo_user = User(
            email="demo@ratham.ai",
            name="Operations Operator",
            password_hash=get_password_hash("demo123"),
            role=UserRole.HOSPITAL_ADMIN,
            is_active=True
        )
        db.add_all([admin_user, coord_user, demo_user])

        # 2. Create Patients
        hospitals = ["Apollo Medical Center", "Fortis Healthcare", "Manipal Hospital", "Max Healthcare", "AIIMS Campus"]
        cities = ["Chennai", "Bengaluru", "Mumbai", "Delhi", "Hyderabad"]
        blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

        patient_records = [
            ("Patient Anitha R.", "O+", "Chennai", "Apollo Medical Center", 19, 18, 7.2, 0.8, 7, 1, 0, 0.82),
            ("Patient Rajesh Kumar", "A+", "Bengaluru", "Manipal Hospital", 21, 24, 6.8, 1.2, 8, 2, 1, 0.75),
            ("Patient Priya Sharma", "B+", "Mumbai", "Fortis Healthcare", 28, 15, 9.4, 0.2, 3, 0, 0, 0.95),
            ("Patient Vikram Singh", "O-", "Delhi", "AIIMS Campus", 14, 13, 7.5, 0.9, 6, 0, 0, 0.90),
            ("Patient Deepa M.", "AB+", "Hyderabad", "Max Healthcare", 21, 20, 8.1, 0.4, 4, 0, 0, 0.88),
            ("Patient Karthik V.", "O+", "Chennai", "Apollo Medical Center", 21, 20, 7.4, 0.7, 6, 1, 0, 0.80),
        ]

        patients = []
        for idx, (name, bg, city, hosp, usual_int, days_since, hb, drop, fatigue, delays, infect, adh) in enumerate(patient_records):
            p_code = f"RTH-P{idx+1001}"
            pred = prediction_service.predict_need({
                "days_since_transfusion": days_since,
                "usual_interval_days": usual_int,
                "hb_level": hb,
                "recent_hb_drop": drop,
                "fatigue_score": fatigue,
                "prior_delay_count": delays,
                "infection_flag": infect,
                "appointment_adherence": adh
            })
            p = Patient(
                patient_code=p_code,
                name=name,
                blood_group=bg,
                city=city,
                hospital_name=hosp,
                transfusion_interval_days=usual_int,
                last_transfusion_date=datetime.now(timezone.utc) - timedelta(days=days_since),
                hb_level=hb,
                recent_hb_drop=drop,
                fatigue_score=fatigue,
                prior_delay_count=delays,
                infection_flag=infect,
                appointment_adherence=adh,
                status=PatientStatus.URGENT if pred["need_probability"] >= 0.6 else PatientStatus.MONITORED,
                risk_level=pred["risk_level"],
                need_probability=pred["need_probability"]
            )
            patients.append(p)
        db.add_all(patients)
        db.commit()

        # 3. Create Donors
        donor_names = [
            ("Arun Prakash", "O+", "Chennai", 4.2, 0.91, 0.08, 1.2, 12, 1),
            ("Bhavna Sundaram", "O+", "Chennai", 7.5, 0.45, 0.52, 6.5, 3, 5),
            ("Chaitanya Rao", "O+", "Chennai", 11.0, 0.78, 0.12, 3.0, 18, 0),
            ("Dinesh Karthik", "A+", "Bengaluru", 3.8, 0.88, 0.05, 1.0, 25, 0),
            ("Elena Joseph", "B+", "Mumbai", 6.2, 0.94, 0.02, 0.8, 40, 0),
            ("Farhan Ahmed", "O-", "Delhi", 9.1, 0.82, 0.15, 2.5, 10, 1),
            ("Gautam Adiga", "AB+", "Hyderabad", 5.0, 0.86, 0.09, 1.8, 15, 0),
            ("Hari Prasad", "O+", "Chennai", 14.5, 0.65, 0.35, 4.2, 2, 3),
        ]

        donors = []
        for idx, (name, bg, city, dist, reach_prob, burn_prob, resp_hrs, last_contact, contacts_14d) in enumerate(donor_names):
            d_code = f"DNR-{idx+101}"
            burn_risk = DonorBurnoutRiskLevel.HIGH_RISK if burn_prob >= 0.5 else (DonorBurnoutRiskLevel.WATCH if burn_prob >= 0.25 else DonorBurnoutRiskLevel.HEALTHY)
            d = Donor(
                donor_code=d_code,
                name=name,
                blood_group=bg,
                phone=f"+91 98400 {idx+10000}",
                city=city,
                latitude=13.0827 + random.uniform(-0.05, 0.05),
                longitude=80.2707 + random.uniform(-0.05, 0.05),
                donation_count=random.randint(2, 12),
                availability_status=DonorAvailabilityStatus.AVAILABLE if burn_prob < 0.6 else DonorAvailabilityStatus.ON_COOLDOWN,
                days_since_last_contact=last_contact,
                contacts_last_30d=contacts_14d * 2,
                contacts_last_14d=contacts_14d,
                response_rate_90d=max(0.2, reach_prob),
                avg_response_hours=resp_hrs,
                distance_km=dist,
                reachability_probability=reach_prob,
                burnout_probability=burn_prob,
                burnout_risk_level=burn_risk
            )
            donors.append(d)
        db.add_all(donors)
        db.commit()

        # 4. Create Initial Emergency Request
        em = EmergencyRequest(
            request_code="RTH-1024",
            patient_id=patients[0].id,
            blood_group="O+",
            units_required=2,
            hospital_name="Apollo Medical Center, Greams Road",
            priority=EmergencyPriority.CRITICAL,
            status=EmergencyStatus.PRIMARY_CONTACTED,
            current_wave=1,
            primary_donor_id=donors[0].id,
            notes="High urgency transfusion prepared for Patient Anitha R."
        )
        db.add(em)
        db.commit()

        # 5. Add Audit Event
        db.add(AuditEvent(
            actor_id="System Seed Script",
            action="DATABASE_INITIALIZED",
            entity_type="SYSTEM",
            entity_id="SEED",
            details={"status": "Operational seed completed successfully."}
        ))
        db.commit()

        print("Operational database successfully seeded with Patients, Donors, Users, and Emergency records.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
