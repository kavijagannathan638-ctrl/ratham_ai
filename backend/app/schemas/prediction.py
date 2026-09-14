from typing import List, Optional
from pydantic import BaseModel

class ExplanationFactor(BaseModel):
    feature: str
    impact: str  # high, medium, low
    direction: str  # increased_risk, decreased_risk, neutral
    description: str

class PredictionNeedResponse(BaseModel):
    need_probability: float
    needs_within_7d: bool
    urgency_score: float
    risk_level: str
    top_factors: List[ExplanationFactor]
    recommendation: str

class PredictionDonorResponse(BaseModel):
    reachability_probability: float
    burnout_probability: float
    reachable: bool
    high_burnout_risk: bool
    reachability_risk_level: str
    burnout_risk_level: str
    expected_response_minutes: float
    top_factors: List[ExplanationFactor]
    recommended_cooldown_days: int
