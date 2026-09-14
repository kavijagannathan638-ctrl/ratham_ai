from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import Base, engine, SessionLocal
from app.ml.registry import registry
from app.api import (
    auth_router,
    patients_router,
    donors_router,
    predictions_router,
    matching_router,
    emergencies_router,
    analytics_router,
    admin_router,
    demo_router,
)
from app.schemas.patient import NeedInputSchema
from app.schemas.donor import DonorInputSchema
from app.schemas.matching import MatchRequestSchema
from app.api.predictions import predict_need as predict_need_v1, predict_reachability as predict_reachability_v1
from app.api.matching import rank_candidates as rank_candidates_v1
from app.api.analytics import get_overview_analytics

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RATHAM AI Modular Monolith Backend...")
    # Create tables automatically on startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas verified.")
    yield
    logger.info("Shutting down RATHAM AI Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler (Section 46)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal operational error occurred. Please contact system administrator.",
                "path": str(request.url.path)
            }
        }
    )

# Health Checks (Section 45)
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "database": "connected",
        "models_loaded": registry.is_healthy()
    }

@app.get("/ready", tags=["Health"])
def readiness_check():
    return {
        "ready": registry.is_healthy(),
        "models": list(registry.models.keys())
    }

# Mount API v1 Routers (Section 19)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(donors_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(matching_router, prefix=settings.API_V1_STR)
app.include_router(emergencies_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

# Legacy Backward-Compatibility API Endpoints
@app.get("/api/dashboard", tags=["Legacy Compatibility"])
def legacy_dashboard():
    db = SessionLocal()
    try:
        return get_overview_analytics(db=db, current_user=None)
    finally:
        db.close()

@app.post("/api/predict/need", tags=["Legacy Compatibility"])
def legacy_predict_need(data: NeedInputSchema):
    return predict_need_v1(data, current_user=None)

@app.post("/api/predict/donor", tags=["Legacy Compatibility"])
def legacy_predict_donor(data: DonorInputSchema):
    return predict_reachability_v1(data, current_user=None)

@app.post("/api/match", tags=["Legacy Compatibility"])
def legacy_match(req: MatchRequestSchema):
    db = SessionLocal()
    try:
        res = rank_candidates_v1(req, db=db, current_user=None)
        return {
            "need": res.need_prediction,
            "primary": res.primary_candidate,
            "backups": res.backup_candidates,
            "policy": res.policy_disclaimer
        }
    finally:
        db.close()
