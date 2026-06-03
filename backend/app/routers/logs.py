from datetime import datetime, timezone
import json, os, io
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import zipfile


from app.schemas.log import LogSchema
from app.schemas.responses import LogIngestResponse, UploadResponse
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


@router.post("/upload")  # remove response_model=UploadResponse if it's there
async def upload_log(
    configuration_id: int = Query(..., description="Evaluation configuration id"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await file.read()

    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e.msg}")

    if isinstance(payload, dict) and isinstance(payload.get("logs"), list):
        payload = payload["logs"]

    try:
        results = log_service.process_uploaded_log(
            configuration_id, payload, file.filename, raw, db
        )
        return {
            "detail": f"Uploaded and processed log(s) for configuration {configuration_id}.",
            "original_path": results.get("original"),
            "derived_by_version": results.get("derived_by_version", {}),
            "schema_warnings": results.get("schema_warnings", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")



@router.post("/register", response_model=LogIngestResponse)
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
        logger.warning(
            "compute_from_log failed for configuration %s: %s",
            configuration_id, repr(e), exc_info=True,
        )
        derived = {"by_metric": {}, "by_pillar": {}, "interaction": {}}
        derived["_warning"] = f"Metric computation failed: {type(e).__name__}"

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
    event_count = len(payload.get("decisions") or [])
    validation_warnings = derived.get("warnings") or []
    return LogIngestResponse(
        detail="Registered log.",
        configuration_id=configuration_id,
        log_id=log_entry.id,
        minio_path=object_name,
        event_count=event_count,
        validation_warnings=validation_warnings,
        derived=derived,
    )


@router.get("/{config_id}")
def list_logs(config_id: int):
    client = get_minio_client()
    prefix = f"{config_id}/"
    objs = client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True)

    keys = [o.object_name for o in objs if o.object_name.endswith(".json")]
    return {"logs": keys}


@router.get("/download/{config_id}")
def get_download_url(config_id: int, object_key: str = Query(...)):
    # Safety check: user can only download within their config prefix
    if not object_key.startswith(f"{config_id}/"):
        raise HTTPException(status_code=400, detail="Invalid object_key for configuration")

    try:
        client = get_minio_client()
        # Optional: check existence to return 404 early
        client.stat_object(MINIO_BUCKET, object_key)

        url = client.presigned_get_object(MINIO_BUCKET, object_key)
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{config_id}/{log_name}")
def remove_log(config_id: int, log_name: str):
    try:
        delete_file(config_id, log_name)
        return {"detail": "Log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/upload-zip")
async def upload_zip(
    configuration_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accepts a ZIP of individual session JSON files (one per application case).
    Merges all logs[] arrays into one aggregated payload and processes normally.
    This is how pilot partners deliver their data.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    raw = await file.read()

    # Extract and merge all JSON files from the zip
    merged_sessions = []
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            json_files = [n for n in zf.namelist()
                         if n.endswith(".json") and not n.startswith("__")]
            if not json_files:
                raise HTTPException(status_code=400,
                                   detail="ZIP contains no JSON files")

            for name in sorted(json_files):
                try:
                    content = json.loads(zf.read(name).decode("utf-8"))
                    # Each file is {"logs": [session]} — unwrap and merge
                    if isinstance(content, dict) and "logs" in content:
                        merged_sessions.extend(content["logs"])
                    elif isinstance(content, dict):
                        merged_sessions.append(content)
                    elif isinstance(content, list):
                        merged_sessions.extend(content)
                except Exception as e:
                    logger.warning("Skipping %s: %s", name, e)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")

    if not merged_sessions:
        raise HTTPException(status_code=400,
                           detail="No valid session data found in ZIP")

    # Repack as aggregated format and process normally
    merged_payload = {"logs": merged_sessions}
    merged_bytes = json.dumps(merged_payload, ensure_ascii=False).encode("utf-8")

    try:
        results = log_service.process_uploaded_log(
            configuration_id,
            merged_sessions,        # already a list
            file.filename,
            merged_bytes,
            db,
        )
        return {
            "detail": f"Merged {len(merged_sessions)} sessions from "
                      f"{len(json_files)} files.",
            "session_count": len(merged_sessions),
            "file_count": len(json_files),
            "original_path": results.get("original"),
            "derived_by_version": results.get("derived_by_version", {}),
            "schema_warnings": results.get("schema_warnings", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
