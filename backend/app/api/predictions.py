from fastapi import APIRouter, Depends
from app.schemas.patient import NeedInputSchema
from app.schemas.donor import DonorInputSchema
from app.schemas.prediction import PredictionNeedResponse, PredictionDonorResponse
from app.ml.inference import prediction_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.post("/need", response_model=PredictionNeedResponse)
def predict_need(data: NeedInputSchema, current_user = Depends(get_current_user)):
    res = prediction_service.predict_need(data.model_dump())
    return res

@router.post("/reachability", response_model=PredictionDonorResponse)
def predict_reachability(data: DonorInputSchema, current_user = Depends(get_current_user)):
    res = prediction_service.predict_donor(data.model_dump())
    return res

@router.post("/burnout", response_model=PredictionDonorResponse)
def predict_burnout(data: DonorInputSchema, current_user = Depends(get_current_user)):
    res = prediction_service.predict_donor(data.model_dump())
    return res
