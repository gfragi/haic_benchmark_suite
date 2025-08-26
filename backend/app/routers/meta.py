from fastapi import APIRouter
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
