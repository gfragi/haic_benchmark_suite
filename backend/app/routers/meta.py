from fastapi import APIRouter
from app.services.seed_core_metrics import seed_core_definitions
import time, os

router = APIRouter()
START = time.time()

@router.get("/health")
def health():
    return {"status": "ok", "uptime_s": round(time.time() - START, 2)}

@router.get("/version")
def version():
    return {
        "service": "haic-benchmark-suite",
        "version": os.getenv("APP_VERSION", "0.3.0-dev"),
        "commit": os.getenv("GIT_COMMIT", "local")
    }

@router.post("/seed/core-metrics")
def seed_core_metrics():
    seed_core_definitions()
    return {"status": "ok"}