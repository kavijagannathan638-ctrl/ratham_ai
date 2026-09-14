from typing import List, Dict, Any, Optional
from app.services.compatibility import is_blood_compatible
from app.ml.inference import prediction_service

class MatchingEngine:
    def __init__(self):
        # Configurable weights summing to 1.0
        self.w_compatibility = 0.30
        self.w_reachability = 0.25
        self.w_availability = 0.15
        self.w_distance = 0.15
        self.w_reliability = 0.10
        self.w_burnout_penalty = 0.05

    def rank_donors(
        self,
        recipient_blood_group: str,
        donors: List[Dict[str, Any]],
        patient_need_pred: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        ranked = []

        for idx, d in enumerate(donors):
            d_bg = d.get("blood_group", "O+")
            avail_status = d.get("availability_status", "AVAILABLE")
            cooldown_days = d.get("cooldown_days_observed", 0)

            # Skip donors currently on mandatory cooldown or permanently unavailable
            if avail_status == "UNAVAILABLE" or avail_status == "ON_COOLDOWN" or cooldown_days > 30:
                continue

            # Check blood compatibility
            compatible = is_blood_compatible(d_bg, recipient_blood_group)
            if not compatible:
                continue  # Operational upstream filter

            # Predict ML reachability and burnout
            pred = prediction_service.predict_donor(d)
            reach_prob = pred["reachability_probability"]
            burn_prob = pred["burnout_probability"]

            distance = float(d.get("distance_km", 5.0))
            resp_rate = float(d.get("response_rate_90d", 0.8))
            avail_rate = float(d.get("availability_rate_90d", 0.85))

            # Compute sub-scores normalized [0, 1]
            dist_score = max(0.0, 1.0 - (distance / 40.0))
            rel_score = min(1.0, max(0.0, resp_rate))
            avail_score = min(1.0, max(0.0, avail_rate))
            comp_score = 1.0

            # Base score calculation
            score = (
                self.w_compatibility * comp_score +
                self.w_reachability * reach_prob +
                self.w_availability * avail_score +
                self.w_distance * dist_score +
                self.w_reliability * rel_score
            )

            # Apply burnout penalty multiplier
            burnout_penalty_applied = False
            if pred["high_burnout_risk"]:
                score *= 0.65
                burnout_penalty_applied = True
            elif burn_prob >= 0.25:
                score *= 0.85

            if not pred["reachable"]:
                score *= 0.55

            why_reasons = [
                f"Compatible blood group ({d_bg} → {recipient_blood_group})",
                f"{int(reach_prob * 100)}% predicted reachability probability",
                f"{distance:.1f} km from hospital destination",
                f"{int(resp_rate * 100)}% historical response rate",
            ]
            if burnout_penalty_applied:
                why_reasons.append("Caution: Burnout risk penalty applied (-35% rank score)")

            ranked.append({
                "rank": 0,
                "donor_id": d.get("id", idx + 1),
                "donor_code": d.get("donor_code", f"DNR-{idx+101}"),
                "name": d.get("name", f"Donor #{idx+1}"),
                "blood_group": d_bg,
                "phone": d.get("phone", "+91 98765 43210"),
                "match_score": round(score, 4),
                "reachability_probability": reach_prob,
                "burnout_probability": burn_prob,
                "distance_km": round(distance, 1),
                "compatibility_score": comp_score,
                "availability_status": avail_status,
                "why_recommended": why_reasons,
                "burnout_penalty_applied": burnout_penalty_applied,
            })

        # Sort descending by match score
        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        for i, r in enumerate(ranked):
            r["rank"] = i + 1

        return ranked

matching_engine = MatchingEngine()
