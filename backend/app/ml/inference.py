from typing import Dict, Any
import numpy as np
from app.ml.registry import registry
from app.ml.explainability import (
    explain_patient_need,
    explain_donor_reachability,
    explain_donor_burnout
)

def arr(d: dict) -> np.ndarray:
    return np.array([list(d.values())], dtype=float)

class PredictionService:
    @staticmethod
    def predict_need(data: Dict[str, Any]) -> Dict[str, Any]:
        values = {
            "days_since_transfusion": float(data.get("days_since_transfusion", 18)),
            "usual_interval_days": float(data.get("usual_interval_days", 21)),
            "hb_level": float(data.get("hb_level", 8.0)),
            "recent_hb_drop": float(data.get("recent_hb_drop", 0.45)),
            "fatigue_score": float(data.get("fatigue_score", 5)),
            "prior_delay_count": float(data.get("prior_delay_count", 0)),
            "infection_flag": float(data.get("infection_flag", 0)),
            "appointment_adherence": float(data.get("appointment_adherence", 0.85)),
        }
        
        need_model = registry.get_model("need_model")
        if need_model:
            prob = float(need_model.predict_proba(arr(values))[0, 1])
        else:
            # Fallback heuristic if model not loaded
            prob = min(0.99, max(0.01, 0.04 * values["days_since_transfusion"] - 0.08 * values["hb_level"] + 0.3 * values["recent_hb_drop"]))

        urgency = min(100.0, max(0.0, 45.0 + 8.0 * values["days_since_transfusion"] - 5.0 * values["hb_level"] + 16.0 * values["recent_hb_drop"] + 5.0 * values["fatigue_score"] + 12.0 * values["infection_flag"]))

        if prob >= 0.8 or urgency >= 80:
            risk_level = "CRITICAL"
        elif prob >= 0.6 or urgency >= 60:
            risk_level = "HIGH"
        elif prob >= 0.35 or urgency >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        factors = explain_patient_need(values, prob)

        recommendation = "Begin donor preparation and reserve candidate slots." if prob >= 0.5 else "Routine monitoring."

        return {
            "need_probability": round(prob, 4),
            "needs_within_7d": prob >= 0.5,
            "urgency_score": round(urgency, 1),
            "risk_level": risk_level,
            "top_factors": factors,
            "recommendation": recommendation,
        }

    @staticmethod
    def predict_donor(data: Dict[str, Any]) -> Dict[str, Any]:
        rcols = [
            "days_since_last_contact", "contacts_last_30d", "response_rate_90d",
            "avg_response_hours", "distance_km", "availability_rate_90d",
            "weekday_availability", "recent_donation_days", "opt_in_active", "night_contact_ratio"
        ]
        bcols = [
            "contacts_last_14d", "contacts_last_30d", "successful_donations_90d",
            "days_since_last_donation", "response_rate_30d", "decline_rate_30d",
            "cooldown_days_observed", "engagement_drop_pct", "avg_response_hours", "voluntary_opt_outs"
        ]

        rd = {c: float(data.get(c, 0)) for c in rcols}
        bd = {c: float(data.get(c, 0)) for c in bcols}

        reach_model = registry.get_model("reachability_model")
        burn_model = registry.get_model("burnout_model")

        if reach_model:
            reach = float(reach_model.predict_proba(arr(rd))[0, 1])
        else:
            reach = max(0.05, min(0.95, data.get("response_rate_90d", 0.8) - 0.01 * data.get("distance_km", 5)))

        if burn_model:
            burn = float(burn_model.predict_proba(arr(bd))[0, 1])
        else:
            burn = min(0.95, max(0.05, 0.08 * data.get("contacts_last_14d", 1) + 0.3 * data.get("decline_rate_30d", 0.1)))

        reach_factors = explain_donor_reachability(rd, reach)
        burn_factors = explain_donor_burnout(bd, burn)

        expected_response_mins = round(max(2.0, rd["avg_response_hours"] * 60.0 * (1.5 if reach < 0.5 else 1.0)), 1)
        
        burn_risk_level = "HIGH_RISK" if burn >= 0.5 else ("WATCH" if burn >= 0.25 else "HEALTHY")
        reach_risk_level = "HIGH" if reach >= 0.75 else ("MEDIUM" if reach >= 0.4 else "LOW")

        cooldown_recommendation = 14 if burn >= 0.5 else (7 if burn >= 0.25 else 0)

        return {
            "reachability_probability": round(reach, 4),
            "burnout_probability": round(burn, 4),
            "reachable": reach >= 0.5,
            "high_burnout_risk": burn >= 0.5,
            "reachability_risk_level": reach_risk_level,
            "burnout_risk_level": burn_risk_level,
            "expected_response_minutes": expected_response_mins,
            "top_factors": reach_factors + burn_factors,
            "recommended_cooldown_days": cooldown_recommendation,
        }

prediction_service = PredictionService()
