from fastapi import APIRouter, Query, HTTPException, Body
from typing import Literal

from pathlib import Path
import json, re
from app.models.api import MetricsList, MetricsEnvelope, ErrorEnvelope
from app.utils.errors import http_error
from metrics_core.interaction_metrics import compute_metrics
import re
from typing import Optional, Dict, Any
from app.models.api import MetricsLoadResponse

router = APIRouter()
METRICS_DIR = Path("metrics").resolve()
FILENAME_RE = re.compile(
    r"^(?P<task>.+?)_(?P<kind>full|summary)_(?P<ts>\d{8}_\d{6}).*\.json$"
)

def _parse_run_filename(name: str) -> dict:
    """
    Parse 'Task_Kind_YYYYMMDD_HHMMSS[...].json' into parts.
    Falls back gracefully if it doesn't match the expected pattern.
    """
    m = FILENAME_RE.match(name)
    if not m:
        return {"file": name, "task": None, "kind": None, "timestamp": None}
    return {
        "file": name,
        "task": m.group("task"),
        "kind": m.group("kind"),
        "timestamp": m.group("ts"),
    }

@router.get("/list", response_model=MetricsList)
def list_metrics(prefix: Optional[str] = Query(None, description="Filter by task prefix")):
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([f.name for f in METRICS_DIR.glob("*.json")])
    if prefix:
        files = [f for f in files if f.startswith(prefix)]
    return {"files": files}




@router.get("/list_by_task", response_model=MetricsList)
def list_by_task(prefix: str = Query(..., description="Task name/prefix (case-insensitive)")):
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"\s+", "_", prefix.strip()).lower()
    files = [f.name for f in METRICS_DIR.glob("*.json") if f.name.lower().startswith(slug)]
    return {"files": sorted(files)}




@router.get("/load", response_model=MetricsLoadResponse,
            responses={404: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}})
def load_metrics(file: str = Query(..., description="Metrics filename under metrics/")):
    path = METRICS_DIR / file
    if not path.exists():
        raise HTTPException(status_code=404, detail="Metrics file not found")

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read metrics: {e}")

    # Normalize: accept either the artifact directly or wrapped under "artifact"
    if "metrics" in data:
        artifact = data
    elif "artifact" in data and isinstance(data["artifact"], dict) and "metrics" in data["artifact"]:
        artifact = data["artifact"]
    else:
        raise HTTPException(status_code=500, detail="No 'metrics' field found in artifact.")

    return {"metrics": artifact["metrics"], "artifact": artifact}

# @router.get("/runs/{task_prefix}")
# def list_runs_by_task(
#     task_prefix: str,
#     kind: Literal["any", "summary", "full"] = Query("any", description="Filter by run kind"),
# ):
#     """
#     List metrics runs whose filename starts with the given task prefix.
#     Examples:
#       /simulator/runs/CT_Scan_Diagnosis
#       /simulator/runs/Kitchen_Toy_Task?kind=summary
#     """
#     METRICS_DIR.mkdir(parents=True, exist_ok=True)

#     # Normalize: spaces → underscores to match file naming convention
#     norm_prefix = task_prefix.replace(" ", "_")

#     # Match ANY file that starts with '<task>_' and ends with .json
#     candidates = sorted(f.name for f in METRICS_DIR.glob(f"{norm_prefix}_*.json"))

#     if kind != "any":
#         candidates = [n for n in candidates if f"_{kind}_" in n]

#     if not candidates:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No runs found for task '{task_prefix}' (kind={kind})."
#         )

#     # Return both filenames and parsed metadata (useful for UI)
#     runs = [_parse_run_filename(n) for n in candidates]
#     return {"task": task_prefix, "kind": kind, "runs": runs}


# @router.get("/runs/{task_prefix}/load")
# def load_runs_by_task(
#     task_prefix: str,
#     kind: Literal["any", "summary", "full"] = "any",
# ):
#     norm_prefix = task_prefix.replace(" ", "_")
#     files = sorted(f for f in METRICS_DIR.glob(f"{norm_prefix}_*.json"))
#     if kind != "any":
#         files = [p for p in files if f"_{kind}_" in p.name]
#     if not files:
#         raise HTTPException(status_code=404, detail=f"No runs found for '{task_prefix}' (kind={kind}).")

#     payload = []
#     for p in files:
#         with open(p, "r") as f:
#             try:
#                 data = json.load(f)
#             except json.JSONDecodeError as e:
#                 # skip malformed files but include an error entry
#                 payload.append({"file": p.name, "error": str(e)})
#                 continue
#         meta = _parse_run_filename(p.name)
#         payload.append({"meta": meta, "data": data})

#     return {"task": task_prefix, "kind": kind, "runs": payload}


@router.post("/compute")
def recompute_metrics(file: str = Query(..., description="Existing artifact to recompute from")):
    path = METRICS_DIR / file
    if not path.exists():
        raise HTTPException(status_code=404, detail="Metrics file not found")
    try:
        with open(path, "r") as f:
            art = json.load(f)
        decisions = art.get("decisions", [])
        T = art.get("T", None)
        baseline_s = art.get("baseline_s", None)
        new_metrics = compute_metrics(decisions=decisions, T=T, baseline_s=baseline_s)
        return {"metrics": new_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recompute: {e}")
