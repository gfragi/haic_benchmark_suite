from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from pathlib import Path
import re
import yaml

from app.models.api import ConfigList, MessageWithPath
from app.utils.errors import http_error, ErrorEnvelope
from haic_env_builder.config_builder.builder import ConfigBuilder
from haic_env_builder.schemas.config import ConfigSchema  # validate early for clear 422s

router = APIRouter()

# ---------- project root detection ----------
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for cand in [*here.parents]:
        if (cand / "backend").is_dir() and (cand / "haic_env_builder").is_dir():
            return cand
    # fallback: go up 3 if structure is standard: repo/backend/app/routers/...
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]

PROJECT_ROOT = _find_project_root()
HAIC_DIR = PROJECT_ROOT / "haic_env_builder" / "configs"
LEGACY_DIR = PROJECT_ROOT / "configs"
CONFIG_DIRS = [HAIC_DIR, LEGACY_DIR]
DEFAULT_WRITE_DIR = HAIC_DIR
for d in CONFIG_DIRS:
    d.mkdir(parents=True, exist_ok=True)

# ---------- helpers ----------
def _slug(s: str) -> str:
    s = s or "task"
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")
    return s or "task"

def _ensure_yaml_suffix(name: str) -> str:
    return name if name.lower().endswith((".yaml", ".yml")) else f"{name}.yaml"

def _is_under(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def _repo_rel_str(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(PROJECT_ROOT))
    except Exception:
        return str(p.resolve())

def _resolve_read_path(name: str) -> Path:
    if not name:
        http_error(400, "MISSING_NAME", "Missing 'name'")

    p = Path(name)

    # absolute under repo
    if p.is_absolute():
        if not _is_under(PROJECT_ROOT, p):
            http_error(400, "OUT_OF_ROOT", "Config path must be under project root", {"path": name})
        if p.exists():
            return p
        http_error(404, "NOT_FOUND", "Config not found", {"name": name})

    # repo-relative
    repo_rel = (PROJECT_ROOT / p)
    if repo_rel.exists():
        return repo_rel

    # basename: search both config dirs
    for base in CONFIG_DIRS:
        cand = base / p.name
        if cand.exists():
            return cand

    http_error(404, "NOT_FOUND", "Config not found", {"name": name})

def _resolve_write_path(filename: Optional[str], default_basename: str) -> Path:
    if filename:
        raw = Path(filename)
        safe_name = _ensure_yaml_suffix(_slug(raw.name))

        # absolute within allowed dirs
        if raw.is_absolute():
            if not _is_under(PROJECT_ROOT, raw):
                http_error(400, "OUT_OF_ROOT", "Config path must be under project root", {"path": filename})
            if any(_is_under(base, raw) for base in CONFIG_DIRS):
                out = raw.with_name(safe_name)
                out.parent.mkdir(parents=True, exist_ok=True)
                return out
            return (DEFAULT_WRITE_DIR / safe_name).resolve()

        # repo-relative within allowed dirs
        repo_rel = (PROJECT_ROOT / raw).resolve()
        if any(_is_under(base, repo_rel) for base in CONFIG_DIRS):
            out = repo_rel.with_name(safe_name)
            out.parent.mkdir(parents=True, exist_ok=True)
            return out

        # bare or disallowed -> preferred dir
        return (DEFAULT_WRITE_DIR / safe_name).resolve()

    # default
    safe_name = _ensure_yaml_suffix(_slug(default_basename))
    return (DEFAULT_WRITE_DIR / safe_name).resolve()

# ---------- models ----------
class ConfigRequest(BaseModel):
    task_name: str = Field(..., description="Scenario name")
    task_description: Optional[str] = Field(None, description="Optional task description")
    task_parameters: Dict[str, Any] = Field(default_factory=dict)
    agent_definitions: List[Dict[str, Any]] = Field(default_factory=list)
    profile_definitions: List[Dict[str, Any]] = Field(default_factory=list)
    filename: Optional[str] = Field(
        None,
        description="Optional file name or path (absolute under project root, repo-relative, or bare). "
                    "Defaults to haic_env_builder/configs/<task>_env.yaml.",
    )

# ---------- routes ----------
@router.post(
    "/generate_config",
    response_model=MessageWithPath,
    responses={422: {"model": ErrorEnvelope}},
    summary="Generate and persist a scenario config YAML",
)
def generate_config(request: ConfigRequest):
    user_choices = {
        "task": {
            "name": request.task_name,
            "description": request.task_description,
            "parameters": request.task_parameters,
        },
        "agents": request.agent_definitions,
        "profiles": request.profile_definitions,
    }

    # early validation for clearer 422s
    try:
        _ = ConfigSchema(**user_choices)
    except Exception as e:
        http_error(422, "VALIDATION_ERROR", "Invalid configuration fields", {"detail": str(e)})

    default_basename = f"{_slug(request.task_name)}_env.yaml"
    out_path = _resolve_write_path(request.filename, default_basename)

    builder = ConfigBuilder()
    builder.build_config(user_choices=user_choices, output_path=str(out_path))

    return {"message": "Environment config generated", "path": _repo_rel_str(out_path)}

@router.get("/list_configs", response_model=ConfigList, summary="List available scenario configs")
def list_configs():
    seen = set()
    items: list[str] = []
    for base in CONFIG_DIRS:
        if base.exists():
            for pattern in ("*.yaml", "*.yml"):
                for f in base.glob(pattern):
                    key = f.resolve()
                    if key in seen:
                        continue
                    seen.add(key)
                    items.append(_repo_rel_str(f))
    items.sort()
    return {"available_configs": items}

@router.get(
    "/load_config",
    responses={404: {"model": ErrorEnvelope}},
    summary="Load a scenario config YAML by name",
)
def load_config(name: str = Query(..., description="YAML filename, repo-relative path, or absolute path under project root")):
    path = _resolve_read_path(name)
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        http_error(404, "NOT_FOUND", "Config not found", {"name": name})
    except Exception as e:
        http_error(400, "MALFORMED_YAML", "Unable to parse YAML", {"detail": str(e), "name": name})
    return {"config": data}
