import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.schemas.ontology import (
    ENTITY_TYPES,
    OntologyDeleteResponse,
    OntologyEntityIn,
    OntologyEntityOut,
    OntologyEntityUpdate,
    OntologyResponse,
    OntologyUsageResponse,
)
from app.services import ontology_service
from app.utils.database import get_db
from app.utils.errors import http_error

router = APIRouter()

# ---------- fit-model: scripts/ isn't a backend package, so it's made
# importable the same way packages/surrogate is in app.routers.simulator
# (sys.path insert, not a real install) - see that module's
# _find_project_root() docstring for why the haic_env_builder/+packages/
# sibling check is used instead of a fixed parents[N] index.
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for cand in here.parents:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
            return cand
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]


PROJECT_ROOT = _find_project_root()
_SCRIPTS_PATH = str(PROJECT_ROOT / "scripts")
if _SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, _SCRIPTS_PATH)

import fit_markov  # noqa: E402

# Fixed structural convention for uploaded "bring your own data" logs -
# matches the payload shape MarkovSurrogate.generate_session() itself
# produces (see packages/surrogate/surrogate/markov.py), so a model fit
# from real data and one fit from that class's own synthetic output use
# the same field paths. Only the *values* at these paths are domain-
# specific; those are auto-discovered per upload (see _discover_action_map).
_AI_ACTION_FIELD = "payload.ai_decision"
_HUMAN_ACTION_FIELD = "payload.op_decision"
_FIT_MODEL_MIN_VALID = 10


def _load_ontology(db: Session) -> Dict[str, Any]:
    """Assembled from ontology_entities (DB-backed, 30s cache) - see
    app.services.ontology_service.get_full_ontology(). Kept as a
    module-level function since app.routers.simulator imports it directly."""
    return ontology_service.get_full_ontology(db)


def _to_out(row) -> OntologyEntityOut:
    return OntologyEntityOut(
        id=row.entity_id, label=row.label, description=row.description,
        status=row.status, properties=row.properties, version=row.version,
    )


@router.get("", response_model=OntologyResponse, summary="Full HAIC ontology (domains, action types, personas, metrics, templates)")
def get_ontology(db: Session = Depends(get_db)):
    return _load_ontology(db)


@router.get("/templates", response_model=List[Dict[str, Any]], summary="Scenario templates only")
def get_templates(db: Session = Depends(get_db)):
    return _load_ontology(db).get("templates", [])


@router.get("/{entity_type}", response_model=List[OntologyEntityOut], summary="List active entities of one type")
def list_entities(entity_type: str, db: Session = Depends(get_db)):
    rows = ontology_service.list_entities(db, entity_type)
    return [_to_out(r) for r in rows]


@router.get("/{entity_type}/{entity_id}/usage", response_model=OntologyUsageResponse, summary="Usage stats for one entity")
def get_entity_usage(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    return ontology_service.get_usage(db, entity_type, entity_id)


@router.get("/{entity_type}/{entity_id}", response_model=OntologyEntityOut, summary="Get one entity")
def get_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    row = ontology_service.get_entity(db, entity_type, entity_id)
    return _to_out(row)


def _slugify_action(raw: str, prefix: str) -> str:
    """'Flagged for verification' -> 'ai_flagged_for_verification'."""
    s = re.sub(r"[^a-z0-9]+", "_", raw.strip().lower()).strip("_")
    return f"{prefix}_{s}" if s else f"{prefix}_unknown"


def _discover_action_map(events: List[dict], actor_value: str, action_field: str, prefix: str) -> Dict[str, str]:
    """Auto-derive a raw-value -> canonical-id map for one side (ai/human)
    by scanning every event with the given actor_type for its value at
    action_field and slugifying each distinct raw value. Uploaded data has
    no pre-declared vocabulary (unlike scripts/fit_markov.py's CLI, which
    takes explicit --ai-action-map/--op-action-map), so it's discovered
    from the file itself."""
    raw_values = {
        fit_markov._get_path(e, action_field)
        for e in events
        if e.get("actor_type") == actor_value and fit_markov._get_path(e, action_field) is not None
    }
    return {raw: _slugify_action(raw, prefix) for raw in sorted(raw_values)}


@router.post("/fit-model", summary="Fit a MarkovSurrogate model from an uploaded HAIC-format log file")
async def fit_model_from_upload(
    file: UploadFile = File(...),
    domain: str = Form(...),
    label: str = Form(...),
    ai_actor_value: str = Form("ai"),
    human_actor_value: str = Form("human"),
    correct_field: str = Form("correct"),
    duration_field: str = Form("duration_s"),
    group_by_field: Optional[str] = Form("payload.op_id"),
    accept_actions: str = Form(...),
    db: Session = Depends(get_db),
):
    raw_bytes = await file.read()
    tmp_path = Path(tempfile.mkstemp(suffix=".json")[1])
    tmp_path.write_bytes(raw_bytes)
    try:
        try:
            data = json.loads(tmp_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            http_error(400, "INVALID_JSON", f"Uploaded file is not valid JSON: {e}")

        try:
            accept_actions_raw = json.loads(accept_actions)
            if not isinstance(accept_actions_raw, list):
                raise ValueError("accept_actions must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            http_error(400, "INVALID_ACCEPT_ACTIONS", f"accept_actions is not a valid JSON array: {e}")

        events = fit_markov._flatten_events(data)
        ai_action_map = _discover_action_map(events, ai_actor_value, _AI_ACTION_FIELD, "ai")
        op_action_map = _discover_action_map(events, human_actor_value, _HUMAN_ACTION_FIELD, "op")
        # accept_actions is supplied as raw decision strings (what the
        # uploader actually sees in their data), not canonical ids -
        # canonicalize through the same map used to fit the model.
        accept_actions_canonical = sorted({
            op_action_map[raw] for raw in accept_actions_raw if raw in op_action_map
        })

        config = {
            "input_data": data,
            "source_label": file.filename,
            "domain": domain,
            "ai_action_field": _AI_ACTION_FIELD,
            "human_action_field": _HUMAN_ACTION_FIELD,
            "ai_actor_value": ai_actor_value,
            "human_actor_value": human_actor_value,
            "correct_field": correct_field,
            "duration_field": duration_field,
            "group_by": group_by_field or None,
            "ai_action_map": ai_action_map,
            "op_action_map": op_action_map,
            "accept_actions": accept_actions_canonical,
        }
        model = fit_markov.fit_model(config)
    finally:
        tmp_path.unlink(missing_ok=True)

    n_valid = model["meta"]["n_valid"]
    if n_valid == 0:
        http_error(400, "NO_VALID_PAIRS", "No valid (ai_event, human_event) pairs found in the uploaded file")
    if n_valid < _FIT_MODEL_MIN_VALID:
        http_error(400, "INSUFFICIENT_DATA",
                   f"Only {n_valid} valid session(s) found - at least {_FIT_MODEL_MIN_VALID} required to fit a model")

    if (model.get("schema") != fit_markov.MODEL_SCHEMA or "aggregate" not in model
            or "ai_actions" not in model or "op_actions" not in model):
        http_error(500, "MODEL_SCHEMA_INVALID", "Fitted model does not match haic.markov_model.v1 schema")

    model_path = f"data/{domain}_markov_model.json"
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    Path(model_path).write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")

    ontology_service.upsert_entity(
        db, "domain", domain, label,
        {"fitted_model": model_path, "example_task": "Fitted from uploaded data"},
    )
    template_id = f"{domain}_fitted"
    ontology_service.upsert_entity(
        db, "template", template_id, f"{label} — Fitted surrogate",
        {
            "domain": domain, "surrogate_tier": 1, "fitted_model": model_path,
            "rt_max_s": 300, "n_items": 50, "n_sessions": 10,
            "metrics": ["Tr", "HCL", "F", "S"],
        },
    )

    return {
        "status": "success",
        "domain": domain,
        "model_path": model_path,
        "n_sessions_fitted": n_valid,
        "ai_actions": model["ai_actions"],
        "op_actions": model["op_actions"],
        "aggregate_tr": model["meta"]["aggregate_accept_rate"],
        "template_id": template_id,
    }


@router.post("/{entity_type}", response_model=OntologyEntityOut, status_code=201, summary="Create an entity")
def create_entity(entity_type: str, payload: OntologyEntityIn, db: Session = Depends(get_db)):
    row = ontology_service.create_entity(db, entity_type, payload)
    return _to_out(row)


@router.put("/{entity_type}/{entity_id}", response_model=OntologyEntityOut, summary="Update an entity")
def update_entity(entity_type: str, entity_id: str, payload: OntologyEntityUpdate, db: Session = Depends(get_db)):
    row = ontology_service.update_entity(db, entity_type, entity_id, payload)
    return _to_out(row)


@router.delete("/{entity_type}/{entity_id}", response_model=OntologyDeleteResponse, summary="Deprecate an entity (soft delete)")
def delete_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    ontology_service.deprecate_entity(db, entity_type, entity_id)
    return OntologyDeleteResponse(message="Entity deprecated", entity_id=entity_id)
