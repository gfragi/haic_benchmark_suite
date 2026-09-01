import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

from app.schemas.ontology import OntologyResponse
from app.utils.errors import http_error

router = APIRouter()

# Mirrors the project-root detection used by routers/simulator.py and
# routers/env_builder.py: checks for haic_env_builder/+packages/ as
# siblings rather than backend/, since the backend/ wrapper directory
# doesn't exist inside the deployed container (Dockerfile.backend copies
# backend/app -> ./app directly).
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for cand in [*here.parents]:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
            return cand
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]


PROJECT_ROOT = _find_project_root()
ONTOLOGY_PATH = PROJECT_ROOT / "data" / "haic_ontology.json"

# Read once at import time (module import happens at app startup) and
# cached for the process lifetime - the ontology is a static data file,
# not something that changes at runtime.
_ontology_cache: Dict[str, Any] | None = None


def _load_ontology() -> Dict[str, Any]:
    global _ontology_cache
    if _ontology_cache is None:
        if not ONTOLOGY_PATH.exists():
            http_error(500, "ONTOLOGY_NOT_FOUND", f"Ontology file not found at {ONTOLOGY_PATH}")
        _ontology_cache = json.loads(ONTOLOGY_PATH.read_text(encoding="utf-8"))
    return _ontology_cache


# Loaded eagerly at import time (startup), per the task's "reads the file
# at startup and caches it" - a lazy fallback in _load_ontology() above
# still covers the (unlikely) case this module is imported before the
# file exists on disk.
_load_ontology()


@router.get("", response_model=OntologyResponse, summary="Full HAIC ontology (domains, action types, personas, metrics, templates)")
def get_ontology():
    return _load_ontology()


@router.get("/templates", response_model=List[Dict[str, Any]], summary="Scenario templates only")
def get_templates():
    return _load_ontology().get("templates", [])
