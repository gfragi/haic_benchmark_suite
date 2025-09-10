from datetime import datetime, timezone
import json, os, io, uuid
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from jsonschema import ValidationError
from sqlalchemy.orm import Session

from app.models import LogEntry
from app.models.configuration import EvaluationConfig
from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.generic_functions import get_config_by_id
from app.utils.minio_utils import upload_file, list_files, download_file, delete_file

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

from app.services.metrics_adapter import compute_from_log
from app.utils.minio_utils import get_minio_client

from app.utils.minio_utils import put_json


router = APIRouter()
logger = logging.getLogger(__name__)
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
minio_client = get_minio_client()

load_dotenv()


@router.post("/upload")
async def upload_log(
    configuration_id: int = Query(..., description="Evaluation configuration id"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1) Read bytes ONCE
    raw = await file.read()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e.msg}")

    # 2) Compute derived (support object or list of objects)
    def _mean_map(dicts, key):
        from statistics import mean
        items = [d.get(key) for d in dicts if isinstance(d, dict)]
        out = {}
        keys = set().union(*(x.keys() for x in items)) if items else set()
        for k in keys:
            vals = [x.get(k) for x in items if isinstance(x.get(k), (int, float))]
            out[k] = mean(vals) if vals else None
        return out

    if isinstance(payload, list):
        derived_list = [compute_from_log(p) for p in payload if isinstance(p, dict)]
        derived = {
            "by_metric": _mean_map(derived_list, "by_metric"),
            "by_pillar": _mean_map(derived_list, "by_pillar"),
            "interaction": _mean_map(derived_list, "interaction"),
        }
    elif isinstance(payload, dict):
        derived = compute_from_log(payload)
    else:
        raise HTTPException(status_code=400, detail="JSON must be an object or an array of objects")

    # 3) Build object names
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    stem = (file.filename.rsplit(".", 1)[0] if file.filename and "." in file.filename
            else (file.filename or f"log-{uuid.uuid4().hex}"))
    orig_name = f"{configuration_id}/uploads/{stem}.{ts}.json"
    derived_name = f"{configuration_id}/uploads/{stem}.{ts}.derived.json"

    # 4) Put both objects to MinIO (no reuse of exhausted stream)
    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=orig_name,
            data=io.BytesIO(raw),
            length=len(raw),
            content_type="application/json",
        )
        enc = json.dumps(derived, ensure_ascii=False, indent=2).encode("utf-8")
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=derived_name,
            data=io.BytesIO(enc),
            length=len(enc),
            content_type="application/json",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO upload failed: {e}")
    
    config = db.query(EvaluationConfig).get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")
    config.minio_path = orig_name
    db.add(config)
    db.commit()
    db.refresh(config)

    return {
        "detail": f"Uploaded and processed log for configuration {configuration_id}.",
        "minio_paths": {"original": orig_name, "derived": derived_name},
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

@router.post("/register", response_model=dict)
def register_log(
    log: LogSchema,
    configuration_id: int = Query(..., description="Evaluation configuration id"),
    db: Session = Depends(get_db),
):
    """
    Accepts JSON directly (no file), computes derived KPIs, stores both JSON and *.derived.json in MinIO,
    updates EvaluationConfig.minio_path, and returns the derived block.
    """
    payload = log.model_dump()

    # 1) Compute derived
    derived = compute_from_log(payload)

    # 2) Build deterministic names
    session_part = payload.get("session_id") or "log"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    original_name = f"uploads/{session_part}.{ts}.json"
    derived_name  = f"uploads/{session_part}.{ts}.derived.json"

    # 3) Store original + derived in MinIO
    put_json(configuration_id, original_name, payload)
    put_json(configuration_id, derived_name, derived)

    # 4) Update config.minio_path to point to the original JSON
    config = db.query(EvaluationConfig).get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")
    config.minio_path = f"{configuration_id}/{original_name}"
    db.add(config)
    db.commit()
    db.refresh(config)

    # 5) Response
    return {
        "detail": "Registered log.",
        "minio_paths": {
            "original": f"{configuration_id}/{original_name}",
            "derived":  f"{configuration_id}/{derived_name}",
        },
        "derived": derived,
    }
