from typing import List, Dict, Any
import numpy as np

def explain_patient_need(values: Dict[str, float], prob: float) -> List[Dict[str, str]]:
    """
    Generates human-understandable explanation factors for 7-day transfusion need prediction.
    """
    factors = []
    
    # Check days since last transfusion relative to usual interval
    days_since = values.get("days_since_transfusion", 0)
    usual_int = values.get("usual_interval_days", 21)
    if days_since >= usual_int:
        factors.append({
            "feature": "days_since_last_transfusion",
            "impact": "high",
            "direction": "increased_risk",
            "description": f"Patient is {days_since} days past last transfusion (usual cycle is {usual_int} days)."
        })
    elif days_since >= usual_int * 0.8:
        factors.append({
            "feature": "days_since_last_transfusion",
            "impact": "medium",
            "direction": "increased_risk",
            "description": f"Patient is approaching expected cycle interval ({days_since}/{usual_int} days)."
        })

    # Check Hemoglobin level
    hb = values.get("hb_level", 8.0)
    if hb <= 7.0:
        factors.append({
            "feature": "hb_level",
            "impact": "high",
            "direction": "increased_risk",
            "description": f"Hemoglobin level is critically low ({hb} g/dL)."
        })
    elif hb <= 8.5:
        factors.append({
            "feature": "hb_level",
            "impact": "medium",
            "direction": "increased_risk",
            "description": f"Hemoglobin level is low ({hb} g/dL)."
        })

    # Check recent Hb drop
    hb_drop = values.get("recent_hb_drop", 0.0)
    if hb_drop >= 0.8:
        factors.append({
            "feature": "recent_hb_drop",
            "impact": "high",
            "direction": "increased_risk",
            "description": f"Accelerated hemoglobin drop detected (-{hb_drop} g/dL recently)."
        })

    # Check fatigue score
    fatigue = values.get("fatigue_score", 1)
    if fatigue >= 7:
        factors.append({
            "feature": "fatigue_score",
            "impact": "medium",
            "direction": "increased_risk",
            "description": f"Reported severe patient fatigue level ({fatigue}/10)."
        })

    # Infection flag
    if values.get("infection_flag", 0) == 1:
        factors.append({
            "feature": "infection_flag",
            "impact": "medium",
            "direction": "increased_risk",
            "description": "Active clinical infection increases transfusion urgency."
        })

    if not factors:
        factors.append({
            "feature": "stable_indicators",
            "impact": "low",
            "direction": "decreased_risk",
            "description": "Patient parameters are currently within expected baseline intervals."
        })

    return factors

def explain_donor_reachability(values: Dict[str, float], prob: float) -> List[Dict[str, str]]:
    """
    Generates explanation factors for donor reachability prediction.
    """
    factors = []
    
    resp_rate = values.get("response_rate_90d", 0.8)
    if resp_rate >= 0.8:
        factors.append({
            "feature": "response_rate_90d",
            "impact": "high",
            "direction": "increased_reachability",
            "description": f"Strong historical response rate ({int(resp_rate*100)}% over last 90 days)."
        })
    elif resp_rate < 0.5:
        factors.append({
            "feature": "response_rate_90d",
            "impact": "high",
            "direction": "decreased_reachability",
            "description": f"Low historical response rate ({int(resp_rate*100)}%)."
        })

    distance = values.get("distance_km", 5.0)
    if distance <= 5.0:
        factors.append({
            "feature": "distance_km",
            "impact": "medium",
            "direction": "increased_reachability",
            "description": f"Close proximity ({distance:.1f} km from hospital)."
        })
    elif distance > 20.0:
        factors.append({
            "feature": "distance_km",
            "impact": "high",
            "direction": "decreased_reachability",
            "description": f"Longer travel distance ({distance:.1f} km from hospital)."
        })

    latency = values.get("avg_response_hours", 2.0)
    if latency <= 1.0:
        factors.append({
            "feature": "avg_response_hours",
            "impact": "medium",
            "direction": "increased_reachability",
            "description": f"Fast average response latency (~{int(latency*60)} minutes)."
        })
    elif latency > 6.0:
        factors.append({
            "feature": "avg_response_hours",
            "impact": "medium",
            "direction": "decreased_reachability",
            "description": f"Delayed response latency (~{latency:.1f} hours)."
        })

    return factors

def explain_donor_burnout(values: Dict[str, float], prob: float) -> List[Dict[str, str]]:
    """
    Generates explanation factors for donor burnout/fatigue risk prediction.
    """
    factors = []
    
    contacts_14d = values.get("contacts_last_14d", 0)
    if contacts_14d >= 4:
        factors.append({
            "feature": "contacts_last_14d",
            "impact": "high",
            "direction": "increased_burnout_risk",
            "description": f"High contact frequency ({contacts_14d} requests in past 14 days)."
        })

    decline_30d = values.get("decline_rate_30d", 0.0)
    if decline_30d >= 0.4:
        factors.append({
            "feature": "decline_rate_30d",
            "impact": "high",
            "direction": "increased_burnout_risk",
            "description": f"Elevated recent decline rate ({int(decline_30d*100)}% declines in last 30 days)."
        })

    drop_pct = values.get("engagement_drop_pct", 0.0)
    if drop_pct >= 20.0:
        factors.append({
            "feature": "engagement_drop_pct",
            "impact": "medium",
            "direction": "increased_burnout_risk",
            "description": f"Notable engagement drop (-{int(drop_pct)}% drop in response speed)."
        })

    if not factors:
        factors.append({
            "feature": "healthy_engagement",
            "impact": "low",
            "direction": "decreased_burnout_risk",
            "description": "Donor contact frequency and response engagement remain healthy."
        })

    return factors
