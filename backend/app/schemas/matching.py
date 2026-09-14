from typing import List, Optional
from pydantic import BaseModel
from app.schemas.patient import NeedInputSchema
from app.schemas.donor import DonorInputSchema

class RankedCandidateSchema(BaseModel):
    rank: int
    donor_id: Optional[int] = None
    donor_code: Optional[str] = None
    name: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    match_score: float
    reachability_probability: float
    burnout_probability: float
    distance_km: float
    compatibility_score: float
    availability_status: str
    why_recommended: List[str]
    burnout_penalty_applied: bool

class MatchRequestSchema(BaseModel):
    patient_id: Optional[int] = None
    patient_input: Optional[NeedInputSchema] = None
    custom_donors: Optional[List[DonorInputSchema]] = None

class MatchResponseSchema(BaseModel):
    need_prediction: dict
    primary_candidate: Optional[RankedCandidateSchema] = None
    backup_candidates: List[RankedCandidateSchema] = []
    policy_disclaimer: str = "Primary donor is never treated as confirmed until explicit response is received."
