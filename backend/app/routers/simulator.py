from fastapi import APIRouter, Query, HTTPException, Depends
from pathlib import Path
from urllib.parse import unquote
from sqlalchemy.orm import Session
import json
import re

from haic_env_builder.utils.simulation_runner import simulate_environment
from app.models.api import SimulationEnvelope
from app.models.configuration import EvaluationConfig
from app.utils.database import get_db
from app.utils.errors import ErrorEnvelope
from app.services.log_service import LogService
from app.services.sim_bridge import translate_sim_run

router = APIRouter()
log_service = LogService()

# ---------- project root detection ----------
def _find_project_root() -> Path:
    """
    Walk up from this file looking for the directory that has both
    haic_env_builder/ and packages/ as siblings. Deliberately does NOT
    require a backend/ subdirectory: in a local repo checkout this file
    lives at backend/app/routers/simulator.py (so "backend" is a real
    sibling of haic_env_builder at the repo root), but Dockerfile.backend
    copies only backend/app -> ./app, dropping the backend/ wrapper
    entirely - inside the deployed container this file lives at
    /app/app/routers/simulator.py with no backend/ directory anywhere,
    which silently broke config resolution (fell through to the
    filesystem root fallback below).
    """
    here = Path(__file__).resolve()
    for cand in [*here.parents]:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
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


# Curated, verified-runnable subset of haic_env_builder/configs/*.yaml.
# Several bundled configs are currently broken and intentionally excluded:
# Radiologist_-_Accept_env.yaml (empty agents:[]), Kitchen_Toy_env.yaml (no
# task.parameters.environment key), My_Environment_v1.yaml/_ui_built.yaml
# (a different, incompatible task_name/agent_definitions schema),
# Overcooked-CrampedRoom_env.yaml (references the retired "overcooked_hcai"
# adapter name - use the _v2 file instead, which uses the current name).
CURATED_SCENARIOS = [
    {
        "id": "CT_Scan_Diagnosis_v2_env",
        "label": "CT Scan Diagnosis (Radiologist + Voice Assistant)",
        "suggested_pilot_tag": "ct_scan_sim",
        "has_human_agent": True,
    },
    {
        "id": "Overcooked-CrampedRoom_v2_env",
        "label": "Overcooked - Cramped Room (two cooperating AI agents, no human)",
        "suggested_pilot_tag": "overcooked_sim",
        "has_human_agent": False,
    },
]


@router.get("/scenarios", summary="List the curated, verified-runnable scenario configs")
def list_scenarios():
    return {"scenarios": CURATED_SCENARIOS}


@router.post(
    "/simulate-and-ingest",
    summary="Run a scenario N times and ingest the results into a configuration",
    description=(
        "Runs the named scenario via simulate_environment() `runs` times "
        "(one distinct seed per run), translates each into an adapter-ready "
        "session, and ingests all of them into `configuration_id` through "
        "the same pipeline real pilot uploads use - so the resulting data "
        "shows up in that configuration's Results Dashboard like any other "
        "upload. Does not trigger evaluation; call POST /evaluate/"
        "{configuration_id} separately, same as after any other upload."
    ),
)
def simulate_and_ingest(
    configuration_id: int = Query(...),
    name: str = Query(..., description="YAML config name or path"),
    pilot_tag: str = Query(...),
    app_version: str = Query("sim_v1.0.0"),
    ai_model_version: str = Query("sim-1.0"),
    runs: int = Query(1, ge=1, le=200),
    seed: int = Query(0, description="Base seed - run i uses seed + i"),
    db: Session = Depends(get_db),
):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration {configuration_id} not found")

    config_path = resolve_config_path(name)

    sessions = []
    for i in range(runs):
        run_result = simulate_environment(str(config_path), seed=seed + i)
        sessions.append(translate_sim_run(
            run_result,
            pilot_tag=pilot_tag,
            app_version=app_version,
            ai_model_version=ai_model_version,
        ))

    merged_bytes = json.dumps({"logs": sessions}, ensure_ascii=False).encode("utf-8")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).stem)

    try:
        results = log_service.process_uploaded_log(
            configuration_id, sessions, f"{stem}.sim", merged_bytes, db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return {
        "detail": f"Simulated and ingested {len(sessions)} session(s) for configuration {configuration_id}.",
        "session_count": len(sessions),
        "configuration_id": configuration_id,
        "derived_by_version": results.get("derived_by_version", {}),
        "schema_warnings": results.get("schema_warnings", []),
    }
