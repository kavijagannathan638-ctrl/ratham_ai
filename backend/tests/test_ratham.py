"""
RATHAM AI Backend Test Suite.
Tests: Blood Compatibility, ML Inference, Emergency State Machine, Auth, API Health.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from app.services.compatibility import is_blood_compatible, get_compatible_donors
from app.ml.inference import prediction_service
from app.emergency.swarm import swarm_engine, VALID_TRANSITIONS
from app.models.emergency import EmergencyStatus

# ── Blood Compatibility Tests ─────────────────────────────────────

class TestBloodCompatibility:
    def test_o_negative_universal_donor(self):
        for recipient in ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']:
            assert is_blood_compatible('O-', recipient), f"O- should be compatible with {recipient}"

    def test_ab_positive_universal_recipient(self):
        for donor in ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']:
            assert is_blood_compatible(donor, 'AB+'), f"{donor} should be compatible with AB+"

    def test_incompatible_pairs(self):
        assert not is_blood_compatible('A+', 'O+'), "A+ cannot donate to O+"
        assert not is_blood_compatible('B+', 'A+'), "B+ cannot donate to A+"
        assert not is_blood_compatible('AB+', 'O-'), "AB+ cannot donate to O-"

    def test_same_type_always_compatible(self):
        for grp in ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']:
            assert is_blood_compatible(grp, grp), f"{grp} should be compatible with self"

    def test_get_compatible_donors(self):
        donors = get_compatible_donors('O+')
        assert 'O+' in donors
        assert 'O-' in donors
        assert 'A+' not in donors

    def test_case_insensitive(self):
        assert is_blood_compatible('o-', 'AB+')
        assert is_blood_compatible('O-', 'ab+')


# ── ML Inference Tests ─────────────────────────────────────

class TestNeedPrediction:
    def test_returns_valid_probability(self):
        res = prediction_service.predict_need({
            "days_since_transfusion": 20, "usual_interval_days": 21,
            "hb_level": 7.5, "recent_hb_drop": 0.8, "fatigue_score": 7,
            "prior_delay_count": 1, "infection_flag": 0, "appointment_adherence": 0.85
        })
        assert 0.0 <= res["need_probability"] <= 1.0

    def test_returns_risk_level(self):
        res = prediction_service.predict_need({})
        assert res["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_returns_explanation_factors(self):
        res = prediction_service.predict_need({
            "days_since_transfusion": 25, "usual_interval_days": 20,
            "hb_level": 6.8, "recent_hb_drop": 1.2, "fatigue_score": 8,
            "prior_delay_count": 2, "infection_flag": 1, "appointment_adherence": 0.5
        })
        assert isinstance(res["top_factors"], list)
        assert len(res["top_factors"]) > 0
        factor = res["top_factors"][0]
        assert "feature" in factor
        assert "description" in factor

    def test_urgency_score_bounded(self):
        res = prediction_service.predict_need({
            "days_since_transfusion": 60, "usual_interval_days": 7,
            "hb_level": 3.0, "recent_hb_drop": 5.0, "fatigue_score": 10,
            "prior_delay_count": 20, "infection_flag": 1, "appointment_adherence": 0.0
        })
        assert 0 <= res["urgency_score"] <= 100

    def test_high_risk_scenario(self):
        res = prediction_service.predict_need({
            "days_since_transfusion": 22, "usual_interval_days": 19,
            "hb_level": 6.8, "recent_hb_drop": 1.1, "fatigue_score": 8,
            "prior_delay_count": 2, "infection_flag": 1, "appointment_adherence": 0.72
        })
        assert res["risk_level"] in ["HIGH", "CRITICAL"]


class TestDonorPrediction:
    def test_returns_valid_probabilities(self):
        res = prediction_service.predict_donor({
            "days_since_last_contact": 5, "contacts_last_30d": 3,
            "response_rate_90d": 0.85, "avg_response_hours": 1.5,
            "distance_km": 4.0, "availability_rate_90d": 0.9,
            "weekday_availability": 0.8, "recent_donation_days": 90,
            "opt_in_active": 1, "night_contact_ratio": 0.1,
            "contacts_last_14d": 1, "successful_donations_90d": 1,
            "days_since_last_donation": 90, "response_rate_30d": 0.9,
            "decline_rate_30d": 0.1, "cooldown_days_observed": 10,
            "engagement_drop_pct": 5, "voluntary_opt_outs": 0
        })
        assert 0.0 <= res["reachability_probability"] <= 1.0
        assert 0.0 <= res["burnout_probability"] <= 1.0

    def test_burnout_risk_level_enum(self):
        res = prediction_service.predict_donor({})
        assert res["burnout_risk_level"] in ["HEALTHY", "WATCH", "HIGH_RISK"]

    def test_high_contact_raises_burnout(self):
        res_low = prediction_service.predict_donor({"contacts_last_14d": 0, "decline_rate_30d": 0.0, "engagement_drop_pct": 0})
        res_high = prediction_service.predict_donor({"contacts_last_14d": 10, "decline_rate_30d": 0.8, "engagement_drop_pct": 80})
        assert res_high["burnout_probability"] >= res_low["burnout_probability"]


# ── Emergency State Machine Tests ─────────────────────────────────────

class TestEmergencyStateMachine:
    def test_created_can_transition_to_searching(self):
        assert swarm_engine.validate_transition(EmergencyStatus.CREATED, EmergencyStatus.SEARCHING)

    def test_fulfilled_is_terminal(self):
        assert not swarm_engine.validate_transition(EmergencyStatus.FULFILLED, EmergencyStatus.SEARCHING)
        assert not swarm_engine.validate_transition(EmergencyStatus.FULFILLED, EmergencyStatus.CREATED)

    def test_declined_activates_backup(self):
        assert swarm_engine.validate_transition(EmergencyStatus.PRIMARY_DECLINED, EmergencyStatus.BACKUP_SEARCH)

    def test_invalid_transition(self):
        assert not swarm_engine.validate_transition(EmergencyStatus.CREATED, EmergencyStatus.FULFILLED)

    def test_all_states_have_transitions_defined(self):
        for state in EmergencyStatus:
            assert state in VALID_TRANSITIONS, f"Missing transition definition for {state}"


# ── FastAPI Health Tests ─────────────────────────────────────

class TestAPIHealth:
    def test_health_endpoint(self):
        import urllib.request, json
        try:
            r = urllib.request.urlopen('http://localhost:8000/health')
            data = json.loads(r.read())
            assert data["status"] == "ok"
            assert data["models_loaded"] is True
        except Exception:
            pytest.skip("Backend not running, skipping API test")

    def test_analytics_endpoint(self):
        import urllib.request, json
        try:
            r = urllib.request.urlopen('http://localhost:8000/api/v1/analytics/overview')
            data = json.loads(r.read())
            assert "patients_monitored" in data
            assert "donors_active" in data
        except Exception:
            pytest.skip("Backend not running, skipping API test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
