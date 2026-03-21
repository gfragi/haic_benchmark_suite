from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.seed_core_metrics import seed_core_definitions
from app.utils.database import get_db
from app.utils.minio_utils import get_minio_client
from app.schemas.responses import HealthResponse
import time, os

router = APIRouter()
START = time.time()


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    db_ok = False
    minio_ok = False

    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    try:
        client = get_minio_client()
        client.list_buckets()
        minio_ok = True
    except Exception:
        pass

    status = "ok" if (db_ok and minio_ok) else "degraded"

    return HealthResponse(
        status=status,
        uptime_s=round(time.time() - START, 2),
        version=os.getenv("APP_VERSION", "0.3.0-dev"),
        db_ok=db_ok,
        minio_ok=minio_ok,
    )

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


@router.get("/adapters")
def list_adapters():
    """
    Return all registered adapter tags plus which ones have a saved config file.
    Used by the frontend to decide whether to show the Pilot Setup form.
    """
    from metrics_core.adapters.registry import AdapterRegistry
    from metrics_core.adapters import config_adapter as ca
    ca.load_all_configs()  # pick up any configs saved after startup
    tags = AdapterRegistry.list_registered()
    builtin = {"generic", "applications", "pilot_apps"}
    return {
        "adapters": [
            {
                "tag": t,
                "source": "builtin" if t in builtin else "config",
            }
            for t in tags
        ]
    }