import json
import tempfile
from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.utils.log_templates import generate_log

router = APIRouter()


@router.get("/generate")
def generate_log_endpoint(
    app_type: str = Query("hmi_xr", description="App type: hmi_xr | radiologist | <custom>"),
    count: int = Query(3, ge=1, le=1000, description="Number of sessions to generate"),
    start_date: str = Query("2025-09-10T13:00:00Z"),
    end_date: str = Query("2025-09-12T13:00:00Z"),
    ai_model_version_range: str = Query("1.0.0-2.0.0"),
    rt_max: float = Query(5.0, description="Max acceptable response time (s) for HCL"),
    baseline_s: float = Query(0.0, description="Baseline task time (s) for EL"),
    app_version: str = Query("1.0.0"),
):
    """
    Returns an array of *adapter-ready* session logs.
    Use /download to fetch a file if you need one.
    """
    logs: List[dict] = [
        generate_log(
            app_type,
            start_date,
            end_date,
            ai_model_version_range,
            rt_max=rt_max,
            baseline_s=baseline_s,
            app_version=app_version,
        )
        for _ in range(count)
    ]

    # Also stash to a temp file for easy manual download/debugging
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(tmp.name, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return {"count": len(logs), "file_path": tmp.name, "logs": logs}


@router.get("/download")
def download_log(file_path: str):
    try:
        return FileResponse(
            path=file_path,
            filename="generated_logs.json",
            media_type="application/json",
        )
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")
