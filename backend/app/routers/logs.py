import datetime
import json, os
import logging
from time import timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.minio_utils import list_files, download_file, delete_file, put_json
from app.services.log_service import LogService
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry
from app.services.metrics_adapter import compute_from_log


router = APIRouter()
logger = logging.getLogger(__name__)
log_service = LogService()


@router.post("/upload")
async def upload_log(
    configuration_id: int = Query(..., description="Evaluation configuration id"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await file.read()

    # Parse JSON
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e.msg}")

    # Unwrap generator wrapper: {count, file_path, logs: [...]}
    if isinstance(payload, dict) and isinstance(payload.get("logs"), list):
        payload = payload["logs"]

    try:
        results = log_service.process_uploaded_log(configuration_id, payload, file.filename, raw, db)
        return {
            "detail": f"Uploaded and processed log(s) for configuration {configuration_id}.",
            "minio_paths": results,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

@router.post("/register", response_model=dict)
def register_log(
    log: LogSchema,
    configuration_id: int = Query(..., description="Evaluation configuration id"),
    db: Session = Depends(get_db),
):
    """
    External services send one session log here.
    We store the log data in the database and create a Log entry linked to the config.
    """
    # 0) Ensure configuration exists
    config = db.get(EvaluationConfig, configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    payload = log.model_dump()

    # 1) Create a Log entry linked to this config with the log data
    # Include decisions in interaction_data since it's not a separate field
    interaction_data = payload.get("interaction_data", {})
    if payload.get("decisions"):
        interaction_data = dict(interaction_data) if interaction_data else {}
        interaction_data["decisions"] = payload.get("decisions")

    log_row = LogEntry(
        configuration_id=configuration_id,
        session_id=payload.get("session_id"),
        user_id=payload.get("user_id"),
        ai_model_version=payload.get("ai_model_version"),
        app_version=payload.get("app_version"),
        start_time=payload.get("start_time"),
        end_time=payload.get("end_time"),
        interaction_data=interaction_data,
        retrain_events=payload.get("retrain_events"),
        performance_infrastructure=payload.get("performance_infrastructure"),
        performance_logs=payload.get("performance_logs"),
        ai_model_data=payload.get("ai_model_data"),
    )
    db.add(log_row)
    db.commit()
    db.refresh(log_row)

    # 2) Per-session derived metrics (optional but nice)
    derived = compute_from_log(payload)

    # 3) Store derived metrics in MinIO for evaluation
    session_part = payload.get("session_id") or "log"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    derived_name = f"uploads/{session_part}.{ts}.derived.json"
    derived_path = f"{configuration_id}/{derived_name}"

    put_json(configuration_id, derived_name, derived)

    # 4) Response back to external service
    return {
        "detail": "Registered log.",
        "configuration_id": configuration_id,
        "log_id": log_row.id,
        "minio_paths": {
            "derived": derived_path,
        },
        "derived": derived,
    }


@router.get("/{config_id}")
def get_logs(config_id: int):
    try:
        return {"logs": list_files(config_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{config_id}/{log_name}")
def get_download_url(config_id: int, log_name: str):
    try:
        return {"download_url": download_file(config_id, log_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_id}/{log_name}")
def remove_log(config_id: int, log_name: str):
    try:
        delete_file(config_id, log_name)
        return {"detail": "Log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
