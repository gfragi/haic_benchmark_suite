from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.generic_functions import get_config_by_id, load_merged_log_for_config, _minio_get_json
from metrics_core import latency_percentiles_by
from typing import Optional

from app.utils.generic_functions import get_config_by_id, load_merged_log_for_config
from metrics_core import human_response_percentiles_by
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


@router.get("/human_rt/pctiles/{configuration_id}")
def human_rt_pctiles(
    configuration_id: int,
    group_key: str = Query("pilot_tag", description="Group by this session field (e.g., pilot_tag, app_version, ai_model_version)"),
    key: Optional[str] = Query(None, description="Exact MinIO key to load (optional)"),
    eq: Optional[str] = Query(None, description="Filter: only sessions where group_key == value"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    cfg = get_config_by_id(configuration_id, db)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if key:
        # use your existing MinIO helper if you exposed it; otherwise let loader handle
        from app.utils.generic_functions import _minio_get_json  # or surface a safe wrapper
        logs_root = _minio_get_json(key)
    else:
        logs_root = load_merged_log_for_config(configuration_id, db)

    if not logs_root or not logs_root.get("logs"):
        raise HTTPException(status_code=404, detail="No logs available for this configuration")

    if eq is not None:
        logs_root["logs"] = [s for s in logs_root["logs"] if str(s.get(group_key, "")) == eq]

    return human_response_percentiles_by(logs_root, group_key=group_key, quantiles=(0.5, 0.9, 0.95))
