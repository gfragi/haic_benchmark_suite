from fastapi import APIRouter, Query, HTTPException, Body
from haic_env_builder.utils.simulation_runner import simulate_environment
from pathlib import Path
import json
import re
from typing import Literal
from haic_env_builder.utils.metrics import compute_metrics

FILENAME_RE = re.compile(
    r"^(?P<task>.+?)_(?P<kind>full|summary)_(?P<ts>\d{8}_\d{6}).*\.json$"
)

router = APIRouter()

METRICS_DIR = Path("metrics").resolve()
CONFIG_DIR = Path("haic_env_builder/configs").resolve()

def _safe_join(base: Path, name: str, expected_suffix: str) -> Path:
    # basic traversal + suffix check
    p = (base / name).resolve()
    if not str(p).startswith(str(base)) or not p.name.endswith(expected_suffix):
        raise HTTPException(status_code=400, detail=f"Invalid file: {name}")
    return p

@router.post("/simulate")
def simulate(
    name: str = Query(..., description="YAML config filename under haic_env_builder/configs/"),
    seed: int | None = Query(None, description="Optional seed for reproducibility"),
):
    try:
        config_path = _safe_join(CONFIG_DIR, name, ".yaml")
        result = simulate_environment(str(config_path), seed=seed)
        return {"simulation_result": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Configuration not found")

@router.get("/list_metrics")
def list_metrics():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(f.name for f in METRICS_DIR.glob("*.json"))
    return {"files": files}

@router.get("/load_metrics")
def load_metrics(file: str = Query(..., description="Metrics filename under metrics/")):
    try:
        path = _safe_join(METRICS_DIR, file, ".json")
        with open(path, "r") as f:
            data = json.load(f)
        return {"metrics": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Malformed JSON: {e}")


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

@router.get("/runs/{task_prefix}")
def list_runs_by_task(
    task_prefix: str,
    kind: Literal["any", "summary", "full"] = Query("any", description="Filter by run kind"),
):
    """
    List metrics runs whose filename starts with the given task prefix.
    Examples:
      /simulator/runs/CT_Scan_Diagnosis
      /simulator/runs/Kitchen_Toy_Task?kind=summary
    """
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # Normalize: spaces → underscores to match file naming convention
    norm_prefix = task_prefix.replace(" ", "_")

    # Match ANY file that starts with '<task>_' and ends with .json
    candidates = sorted(f.name for f in METRICS_DIR.glob(f"{norm_prefix}_*.json"))

    if kind != "any":
        candidates = [n for n in candidates if f"_{kind}_" in n]

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail=f"No runs found for task '{task_prefix}' (kind={kind})."
        )

    # Return both filenames and parsed metadata (useful for UI)
    runs = [_parse_run_filename(n) for n in candidates]
    return {"task": task_prefix, "kind": kind, "runs": runs}


@router.get("/runs/{task_prefix}/load")
def load_runs_by_task(
    task_prefix: str,
    kind: Literal["any", "summary", "full"] = "any",
):
    norm_prefix = task_prefix.replace(" ", "_")
    files = sorted(f for f in METRICS_DIR.glob(f"{norm_prefix}_*.json"))
    if kind != "any":
        files = [p for p in files if f"_{kind}_" in p.name]
    if not files:
        raise HTTPException(status_code=404, detail=f"No runs found for '{task_prefix}' (kind={kind}).")

    payload = []
    for p in files:
        with open(p, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                # skip malformed files but include an error entry
                payload.append({"file": p.name, "error": str(e)})
                continue
        meta = _parse_run_filename(p.name)
        payload.append({"meta": meta, "data": data})

    return {"task": task_prefix, "kind": kind, "runs": payload}


@router.post("/compute_metrics")
def compute_from_decisions(payload: dict = Body(...)):
    """
    Compute metrics from raw decisions (no need to run the simulator).
    Body:
      {
        "decisions": [ { ... }, ... ]
      }
    """
    decisions = payload.get("decisions", [])
    if not isinstance(decisions, list) or not decisions:
        raise HTTPException(status_code=400, detail="Body must include non-empty 'decisions' list.")
    return {"metrics": compute_metrics(decisions)}
