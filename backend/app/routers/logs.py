from datetime import datetime, timezone
import json, os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.minio_utils import get_minio_client, list_files, download_file, delete_file, put_json
from app.services.log_service import LogService
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry
from app.services.metrics_adapter import compute_from_log
from app.services.evaluate import _normalize_logs_data


router = APIRouter()
logger = logging.getLogger(__name__)
log_service = LogService()
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

minio_client = get_minio_client()


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
    We append it to the aggregated log file in MinIO (config.minio_path).
    If it's the first log, we create that file.
    We also create a LogEntry row and return derived KPIs for this session.
    """
    if not MINIO_BUCKET:
        raise HTTPException(status_code=500, detail="MINIO_BUCKET env var is missing.")

    # 0) Ensure configuration exists
    config = db.get(EvaluationConfig, configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    payload = log.model_dump()

    # 1) Compute per-session derived KPIs (optional but useful in response)
    try:
        derived = compute_from_log(payload)
    except Exception as e:
        print(f"[logs/register] compute_from_log failed: {repr(e)}")
        derived = {"by_metric": {}, "by_pillar": {}, "interaction": {}}

    # 2) Load existing aggregated logs from MinIO (if any)
    aggregated_entries: list[dict]

    if config.minio_path:
        # There is already a log file for this config; load + append
        try:
            obj = minio_client.get_object(MINIO_BUCKET, config.minio_path)
            raw_bytes = obj.read()
        finally:
            try:
                obj.close()
                obj.release_conn()
            except Exception:
                pass

        try:
            existing_json = json.loads(raw_bytes.decode("utf-8"))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Existing log at '{config.minio_path}' is not valid JSON: {e}",
            )

        # Normalize using the same function as in run_evaluation
        try:
            entries = _normalize_logs_data(existing_json)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to normalize existing logs: {e}",
            )

        aggregated_entries = entries + [payload]

        # We'll overwrite the same object with the updated list
        object_name = config.minio_path

    else:
        # First log for this configuration: create new list
        aggregated_entries = [payload]
        # use a stable name, similar to upload_file: "<config_id>/config_<id>.json"
        filename = f"config_{configuration_id}.json"
        object_name = f"{configuration_id}/{filename}"
        config.minio_path = object_name  # this is what run_evaluation uses

    # 3) Save updated aggregated logs back to MinIO
    encoded = json.dumps(aggregated_entries, ensure_ascii=False, indent=2).encode("utf-8")
    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=io.BytesIO(encoded),
        length=len(encoded),
        content_type="application/json",
    )

    # 4) Create LogEntry row for this session (for auditing/inspection)
    log_entry = LogEntry(
        configuration_id=configuration_id,
        session_id=payload.get("session_id"),
        user_id=payload.get("user_id"),
        ai_model_version=payload.get("ai_model_version"),
        app_version=payload.get("app_version"),
        start_time=payload.get("start_time"),
        end_time=payload.get("end_time"),
        interaction_data=payload.get("interaction_data"),
        retrain_events=payload.get("retrain_events"),
        performance_infrastructure=payload.get("performance_infrastructure"),
        performance_logs=payload.get("performance_logs"),
        ai_model_data=payload.get("ai_model_data"),
    )
    db.add(log_entry)
    db.add(config)
    db.commit()
    db.refresh(log_entry)

    # 5) Response
    return {
        "detail": "Registered log.",
        "configuration_id": configuration_id,
        "log_id": log_entry.id,
        "minio_path": object_name,     # this is exactly what run_evaluation will use
        "derived": derived,            # per-session KPIs, if compute_from_log is used
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
