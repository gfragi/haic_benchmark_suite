import asyncio
import logging
import os
import sys
import traceback
from fastapi import APIRouter, Query, HTTPException, Depends, BackgroundTasks
from pathlib import Path
from urllib.parse import unquote
from sqlalchemy.orm import Session
import json
import re

from haic_env_builder.utils.simulation_runner import simulate_environment
from app.models.api import SimulationEnvelope
from app.models.configuration import EvaluationConfig
from app.routers.evaluate import _safe_evaluate
from app.routers.ontology import _load_ontology
from app.schemas.ontology import SimulateProbabilisticRequest, SimulateProbabilisticResponse
from app.utils.database import get_db
from app.utils.errors import ErrorEnvelope, http_error
from app.services.log_service import LogService
from app.services.sim_bridge import translate_sim_run
from app.services import ontology_service

router = APIRouter()
log_service = LogService()
logger = logging.getLogger(__name__)

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


# ---------- probabilistic (ontology-driven) simulation ----------

_MARKOV_SURROGATE_PATH = str(PROJECT_ROOT / "packages" / "surrogate")
if _MARKOV_SURROGATE_PATH not in sys.path:
    sys.path.insert(0, _MARKOV_SURROGATE_PATH)

_HAIC_DEBUG = os.getenv("HAIC_DEBUG", "false").lower() in {"1", "true", "yes", "on"}


def _validate_probabilistic_request(request: SimulateProbabilisticRequest, ontology: dict) -> str | None:
    """
    Runs the pre-execution checks from the task spec. Returns the resolved
    fitted_model path for tier 1 (or None for other tiers). Raises a 422
    via http_error() on the first failing check.
    """
    domains_by_id = {d["id"]: d for d in ontology.get("domains", [])}
    if request.domain not in domains_by_id:
        http_error(422, "UNKNOWN_DOMAIN", f"Unknown domain '{request.domain}'",
                   {"known_domains": list(domains_by_id.keys())})

    if not (0 <= request.surrogate_tier <= 3):
        http_error(422, "INVALID_TIER", "surrogate_tier must be between 0 and 3")

    if request.n_items <= 0 or request.n_sessions <= 0:
        http_error(422, "INVALID_COUNTS", "n_items and n_sessions must be positive")

    known_metrics = {m["id"] for m in ontology.get("metric_families", [])}
    unknown = set(request.metrics) - known_metrics
    if unknown:
        http_error(422, "UNKNOWN_METRICS", f"Unknown metric(s): {sorted(unknown)}",
                   {"known_metrics": sorted(known_metrics)})

    fitted_model = None
    if request.surrogate_tier == 1:
        fitted_model = request.fitted_model or domains_by_id[request.domain].get("fitted_model")
        if not fitted_model:
            http_error(422, "MISSING_FITTED_MODEL",
                       f"surrogate_tier=1 requires a fitted_model - none provided and domain "
                       f"'{request.domain}' has none in the ontology")
    return fitted_model


def _compute_sc_weighted_baseline(model_path: str) -> float | None:
    """
    Weighted-mean 'no-AI baseline' approximation: sum over ai_action of
    ai_action_frequency * duration_stats[ai_action].mean (ai_accept
    contributes 0 - its frequency is always 0, see fit_markov_sc.py, so it
    doesn't need special-casing here).

    Same caveat as the identical formula in scripts/validate_surrogate.py:
    this actually averages the WITH-AI operator review time, not a genuine
    without-AI baseline - there's no real without-AI measurement in this
    dataset. Treat it as a rough approximation, not ground truth.
    """
    try:
        model = json.loads(Path(model_path).read_text(encoding="utf-8"))
    except Exception:
        return None
    agg = model.get("aggregate", {})
    freq = agg.get("ai_action_frequency") or {}
    stats = agg.get("duration_stats") or {}
    total = 0.0
    for ai_action, f in freq.items():
        d = stats.get(ai_action)
        if d and d.get("mean") is not None:
            total += f * d["mean"]
    return total if total > 0 else None


def _resolve_baseline(request: SimulateProbabilisticRequest, fitted_model: str | None) -> tuple[float | None, list[str]]:
    """
    Resolve the baseline_s to thread through to evaluation, plus any
    warnings about metrics that won't be computable as a result.

    Priority: caller-supplied > Smart-City-tier-1 weighted-mean fallback
    (the only domain with a fitted model today, so the only one this can
    compute anything for) > none, with a warning noting EL will be null.
    """
    if request.baseline_s is not None:
        return request.baseline_s, []
    if request.domain == "smart_city" and request.surrogate_tier == 1:
        baseline = _compute_sc_weighted_baseline(fitted_model or "data/sc_markov_model.json")
        if baseline is not None:
            return baseline, []
    return None, [f"EL not computed: baseline_s not provided for domain {request.domain}"]


def _apply_metric_meta(sessions: list[dict], rt_max_s: float, baseline_s: float | None) -> None:
    """
    Thread rt_max_s/baseline_s into each session's meta.task_parameters -
    the existing per-session override channel _derive_rt_max()/
    _derive_baseline_s() (backend/app/services/metrics_adapter.py) already
    check ahead of P95 auto-derivation. Reusing that channel means the
    evaluate endpoint itself needs no changes and non-surrogate uploads
    are entirely unaffected.
    """
    for s in sessions:
        tp = s.setdefault("meta", {}).setdefault("task_parameters", {})
        tp["rt_max"] = rt_max_s
        if baseline_s is not None:
            tp["baseline_s"] = baseline_s


def _run_tier0_sync(
    request: SimulateProbabilisticRequest, baseline_s: float | None, db: Session,
) -> tuple[list[str], int]:
    """Scripted (tier 0) path - same underlying mechanism as
    POST /simulator/simulate-and-ingest, inlined here (rather than called
    directly) so exact per-session decision counts can be reported back,
    which that endpoint's response doesn't expose."""
    config_path = resolve_config_path(request.name)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(request.name).stem)

    sessions, run_ids = [], []
    for i in range(request.n_sessions):
        seed = request.seed + i
        run_result = simulate_environment(str(config_path), seed=seed)
        sessions.append(translate_sim_run(
            run_result, pilot_tag=request.pilot_tag,
            app_version=request.app_version, ai_model_version=request.ai_model_version,
        ))
        run_ids.append(f"{stem}_{seed}")

    _apply_metric_meta(sessions, request.rt_max_s, baseline_s)

    n_decisions = sum(len(s["decisions"]) for s in sessions)
    merged_bytes = json.dumps({"logs": sessions}, ensure_ascii=False).encode("utf-8")
    log_service.process_uploaded_log(request.configuration_id, sessions, f"{stem}.sim", merged_bytes, db)
    return run_ids, n_decisions


def _run_tier1_sync(
    request: SimulateProbabilisticRequest, fitted_model: str, baseline_s: float | None, db: Session,
) -> tuple[list[str], int]:
    """Markov-chain (tier 1) path: MarkovSurrogateSC.generate_batch() then
    ingest through the same process_uploaded_log() real uploads use."""
    from surrogate.markov_sc import MarkovSurrogateSC

    if not Path(fitted_model).exists():
        http_error(400, "FITTED_MODEL_NOT_FOUND", f"fitted_model file not found: {fitted_model}")

    surrogate = MarkovSurrogateSC(model_path=fitted_model, persona=request.persona, seed=request.seed)
    sessions = surrogate.generate_batch(
        n_sessions=request.n_sessions, n_items=request.n_items,
        rt_max_s=request.rt_max_s, baseline_s=request.baseline_s,
    )

    run_ids = [s["run_id"] for s in sessions]
    n_decisions = sum(len(s["decisions"]) for s in sessions)

    # MarkovSurrogateSC's own artifact bakes in its own static
    # pilot_tag/app_version/ai_model_version under meta.* - override at the
    # top level (schema_bridge checks top-level fields before falling back
    # to meta.*) so the caller's requested values actually take effect,
    # without needing to touch markov_sc.py itself.
    for s in sessions:
        s["pilot_tag"] = request.pilot_tag
        s["app_version"] = request.app_version
        s["ai_model_version"] = request.ai_model_version

    _apply_metric_meta(sessions, request.rt_max_s, baseline_s)

    stem = f"markov_{request.domain}_{request.persona}"
    merged_bytes = json.dumps({"logs": sessions}, ensure_ascii=False).encode("utf-8")
    log_service.process_uploaded_log(request.configuration_id, sessions, f"{stem}.sim", merged_bytes, db)
    return run_ids, n_decisions


@router.post(
    "/probabilistic",
    response_model=SimulateProbabilisticResponse,
    responses={
        422: {"model": ErrorEnvelope}, 400: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope}, 501: {"model": ErrorEnvelope},
    },
    summary="Run an ontology-driven probabilistic surrogate and ingest the results",
    description=(
        "Tier 0 delegates to the same scripted mechanism as "
        "/simulator/simulate-and-ingest. Tier 1 runs MarkovSurrogateSC. "
        "Tiers 2-3 are planned but not yet implemented (501). Ingestion "
        "uses the same process_uploaded_log() pipeline as every other "
        "upload; evaluation is then triggered as a background task, same "
        "as POST /evaluate/{configuration_id}."
    ),
)
async def simulate_probabilistic(
    request: SimulateProbabilisticRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ontology = _load_ontology(db)
    fitted_model = _validate_probabilistic_request(request, ontology)

    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == request.configuration_id).first()
    if not config:
        http_error(400, "CONFIGURATION_NOT_FOUND", f"Configuration {request.configuration_id} not found")

    if request.surrogate_tier >= 2:
        http_error(501, "TIER_NOT_IMPLEMENTED",
                   f"Tier {request.surrogate_tier} surrogate is planned but not yet available.")

    effective_baseline_s, warnings = _resolve_baseline(request, fitted_model)

    loop = asyncio.get_event_loop()
    try:
        if request.surrogate_tier == 0:
            run_ids, n_decisions = await loop.run_in_executor(None, _run_tier0_sync, request, effective_baseline_s, db)
        else:
            run_ids, n_decisions = await loop.run_in_executor(
                None, _run_tier1_sync, request, fitted_model, effective_baseline_s, db,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Probabilistic simulation failed for config %s: %s",
                     request.configuration_id, repr(e), exc_info=True)
        detail = f"Surrogate generation failed: {e}\n{traceback.format_exc()}" if _HAIC_DEBUG else "Surrogate generation failed."
        http_error(500, "GENERATION_FAILED", detail)

    for run_id in run_ids:
        ontology_service.record_usage(db, run_id, "domain", request.domain, "domain")
        ontology_service.record_usage(db, run_id, "persona_archetype", request.persona, "persona")

    background_tasks.add_task(_safe_evaluate, request.configuration_id)

    return SimulateProbabilisticResponse(
        status="success",
        n_sessions_generated=request.n_sessions,
        n_decisions_total=n_decisions,
        surrogate_tier=request.surrogate_tier,
        persona=request.persona,
        run_ids=run_ids,
        pilot_tag=request.pilot_tag,
        warnings=warnings,
    )
