from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.generic_functions import get_config_by_id, load_merged_log_for_config
from metrics_core import latency_percentiles_by
from typing import Optional

router = APIRouter()

@router.get("/latency/pctiles/{configuration_id}")
def latency_pctiles(
    configuration_id: int,
    group_key: str = Query("ai_model_version"),
    key: str | None = Query(None, description="Exact MinIO key to load (e.g. '3/uploads/events.20260107T102233.abcd1234.json')"),
    eq: str | None = Query(None),
    db: Session = Depends(get_db),
):
    cfg = get_config_by_id(configuration_id, db) or \
          HTTPException(status_code=404, detail="Configuration not found")

    if key:
        logs_root = _minio_get_json(key)  # use your existing minio client helper
    else:
        logs_root = load_merged_log_for_config(configuration_id, db)

    if not logs_root or not logs_root.get("logs"):
        raise HTTPException(status_code=404, detail="No logs available for this configuration")

    if eq is not None:
        logs_root["logs"] = [s for s in logs_root["logs"] if str(s.get(group_key, "")) == eq]

    return latency_percentiles_by(logs_root, group_key=group_key, quantiles=(0.5, 0.9, 0.95))

