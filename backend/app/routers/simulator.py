from fastapi import APIRouter, Query, HTTPException, Body
from haic_env_builder.utils.simulation_runner import simulate_environment
from pathlib import Path
import json
import re
from app.models.api import SimulationEnvelope, ErrorEnvelope
from app.utils.errors import http_error
from app.models.api import MetricsList, ErrorEnvelope


router = APIRouter()

METRICS_DIR = Path("metrics").resolve()
CONFIG_DIR = Path("haic_env_builder/configs").resolve()

def _safe_join(base: Path, name: str, expected_suffix: str | tuple[str, ...]) -> Path:
    p = (base / name).resolve()
    if not str(p).startswith(str(base)) or not p.name.endswith(expected_suffix):
        raise HTTPException(status_code=400, detail=f"Invalid file: {name}")
    return p

@router.post(
    "/simulate",
    response_model=SimulationEnvelope,
    responses={404: {"model": ErrorEnvelope}},
    summary="Run a simulation using a stored YAML config",
    description="Executes the environment defined in a YAML config and returns decisions + metrics."
)
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

@router.get("/runs")
def list_runs():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(f.name for f in METRICS_DIR.glob("*.json"))
    return {"files": files}

@router.get("/runs/{file}", response_model=dict, responses={404: {"model": ErrorEnvelope}}, summary="Load metrics from a simulation run", description="Fetches and returns the metrics stored in a specified JSON file.")
def load_run(file: str):
    try:
        path = _safe_join(METRICS_DIR, file, ".json")
        with open(path, "r") as f:
            data = json.load(f)
        return {"metrics": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Malformed JSON: {e}")


# Filter by task name
@router.get("/runs_by_task", response_model=MetricsList, summary="List simulation run files filtered by task name", description="Returns a list of JSON files whose names start with the specified task name or prefix (case-insensitive).")
def list_runs_by_task(prefix: str = Query(..., description="Task name/prefix (case-insensitive)")):
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"\s+", "_", prefix.strip()).lower()
    files = [f.name for f in METRICS_DIR.glob("*.json") if f.name.lower().startswith(slug)]
    return {"files": sorted(files)}