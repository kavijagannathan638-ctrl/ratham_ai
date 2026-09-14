from typing import List, Dict, Any
from pydantic import BaseModel

class OverviewAnalytics(BaseModel):
    patients_monitored: int
    high_risk_patients: int
    donors_active: int
    available_donors: int
    at_risk_donors: int
    active_emergencies: int
    donor_response_rate: float
    requests_fulfilled: int
    avg_fulfillment_time_minutes: float
    blood_demand_trend: List[Dict[str, Any]]
    reachability_distribution: List[Dict[str, Any]]
    burnout_distribution: List[Dict[str, Any]]
