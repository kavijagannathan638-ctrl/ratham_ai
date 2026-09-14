from app.api.auth import router as auth_router
from app.api.patients import router as patients_router
from app.api.donors import router as donors_router
from app.api.predictions import router as predictions_router
from app.api.matching import router as matching_router
from app.api.emergencies import router as emergencies_router
from app.api.analytics import router as analytics_router
from app.api.admin import router as admin_router
from app.api.demo import router as demo_router

__all__ = [
    "auth_router",
    "patients_router",
    "donors_router",
    "predictions_router",
    "matching_router",
    "emergencies_router",
    "analytics_router",
    "admin_router",
    "demo_router"
]
