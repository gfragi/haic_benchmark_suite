from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from urllib.parse import unquote
import json
import re

from haic_env_builder.utils.simulation_runner import simulate_environment
from app.models.api import SimulationEnvelope, ErrorEnvelope

# HAIC Sim MVP imports
try:
    from haic_sim_mvp.engine.run_sim import run_from_config
    HAIC_SIM_AVAILABLE = True
except ImportError:
    HAIC_SIM_AVAILABLE = False

router = APIRouter()

# ---------- project root detection ----------
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for cand in [*here.parents]:
        if (cand / "backend").is_dir() and (cand / "haic_env_builder").is_dir():
            return cand
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]

PROJECT_ROOT = _find_project_root()
CONFIG_DIRS = [
    PROJECT_ROOT / "haic_env_builder" / "configs",
    PROJECT_ROOT / "configs",
]

RUNS_DIR = (PROJECT_ROOT / "runs").resolve()
RUNS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- helpers ----------
def _safe_join(base: Path, name: str, expected_suffix: str | tuple[str, ...]) -> Path:
    p = (base / name).resolve()
    if not str(p).startswith(str(base)) or not p.name.endswith(expected_suffix):
        raise HTTPException(status_code=400, detail=f"Invalid file: {name}")
    return p

def resolve_config_path(name: str) -> Path:
    """
    Accepts:
      - absolute path inside the repo
      - repo-relative path (e.g., haic_env_builder/configs/foo.yaml or configs/foo.yaml)
      - bare filename (looks up in known config dirs)
    """
    name = unquote(name or "")
    if not name:
        raise HTTPException(status_code=400, detail="Missing 'name'")

    p = Path(name)

    # absolute under repo
    if p.is_absolute():
        try:
            p.resolve().relative_to(PROJECT_ROOT)
        except ValueError:
            raise HTTPException(status_code=400, detail="Config path must be under the project root")
        if p.exists():
            return p
        raise HTTPException(status_code=404, detail=f"Config not found: {p}")

    # repo-relative
    repo_rel = (PROJECT_ROOT / p)
    if repo_rel.exists():
        return repo_rel

    # basename: search known dirs
    for base in CONFIG_DIRS:
        cand = base / p.name
        if cand.exists():
            return cand

    raise HTTPException(status_code=404, detail=f"Config not found: {name}")

# ---------- routes ----------
@router.post(
    "/simulate",
    response_model=SimulationEnvelope,
    responses={404: {"model": ErrorEnvelope}},
    summary="Run a simulation using a stored YAML config",
    description="Executes the environment defined in a YAML config and returns decisions + metrics."
)
def simulate(
    name: str = Query(..., description="YAML config name or path"),
    seed: int | None = Query(None, description="Optional seed for reproducibility"),
):
    config_path = resolve_config_path(name)
    result = simulate_environment(str(config_path), seed=seed)
    return {"simulation_result": result}

@router.get("/runs")
def list_runs():
    files = sorted(f.name for f in RUNS_DIR.glob("*.json"))
    return {"files": files}

@router.get(
    "/runs/{file}",
    response_model=dict,
    responses={404: {"model": ErrorEnvelope}},
    summary="Load metrics from a simulation run",
    description="Fetches and returns the metrics stored in a specified JSON file."
)
def load_run(file: str):
    try:
        path = _safe_join(RUNS_DIR, file, (".json",))
        with open(path, "r") as f:
            data = json.load(f)
        return {"metrics": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Malformed JSON: {e}")

@router.get(
    "/runs_by_task",
    summary="List simulation run files filtered by task name",
    description="Returns a list of JSON files whose names start with the specified task name or prefix (case-insensitive)."
)
def list_runs_by_task(prefix: str = Query(..., description="Task name/prefix (case-insensitive)")):
    slug = re.sub(r"\s+", "_", prefix.strip()).lower()
    files = [f.name for f in RUNS_DIR.glob("*.json") if f.name.lower().startswith(slug)]
    return {"files": sorted(files)}

@router.post(
    "/simulate_haic",
    summary="Run a HAIC Sim MVP simulation directly from JSON config",
    description="Executes a HAIC Sim MVP simulation using the provided JSON configuration."
)
def simulate_haic(
    config: dict,
    seed: int | None = Query(None, description="Optional seed for reproducibility"),
):
    if not HAIC_SIM_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HAIC Sim MVP not available. Please check installation."
        )

    # Run the HAIC simulation
    try:
        results_dir = str(PROJECT_ROOT / "haic_sim_mvp" / "results")
        output_path = run_from_config(config, results_dir=results_dir)

        # Load and return the results
        with open(output_path, "r") as f:
            result = json.load(f)

        return {"simulation_result": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"HAIC simulation failed: {str(e)}"
        )
