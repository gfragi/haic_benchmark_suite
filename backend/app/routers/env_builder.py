from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from pathlib import Path
import re
import yaml

from app.models.api import ConfigList, MessageWithPath, ErrorEnvelope
from app.utils.errors import http_error
from haic_env_builder.config_builder.builder import ConfigBuilder
from haic_env_builder.schemas.config import ConfigSchema  # validate early for clear 422s

router = APIRouter()

# Where YAML configs are stored
CONFIG_DIR = Path("configs").resolve()
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def _slug(s: str) -> str:
    s = s or "task"
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")
    return s or "task"

def _safe_config_path(filename: str) -> Path:
    """Ensure filename is a simple .yaml under CONFIG_DIR (no traversal)."""
    name = _slug(filename)
    if not name.endswith(".yaml"):
        name = f"{name}.yaml"
    p = (CONFIG_DIR / name).resolve()
    if not str(p).startswith(str(CONFIG_DIR)):
        http_error(400, "INVALID_PATH", "Invalid config path", {"path": filename})
    return p

# Request model (keeps your existing field names)
class ConfigRequest(BaseModel):
    task_name: str = Field(..., description="Scenario name")
    task_description: Optional[str] = Field(None, description="Optional task description")
    task_parameters: Dict[str, Any] = Field(default_factory=dict, description="Task.parameters (environment, env_params, etc.)")
    agent_definitions: List[Dict[str, Any]] = Field(default_factory=list, description="List of agent dicts")
    profile_definitions: List[Dict[str, Any]] = Field(default_factory=list, description="List of profile dicts")
    filename: Optional[str] = Field(None, description="Optional filename override (will be slugged and suffixed with .yaml)")

@router.post(
    "/generate_config",
    response_model=MessageWithPath,
    responses={422: {"model": ErrorEnvelope}},
    summary="Generate and persist a scenario config YAML",
)
def generate_config(request: ConfigRequest):
    # Build a user_choices payload shaped like ConfigSchema
    user_choices = {
        "task": {
            "name": request.task_name,
            "description": request.task_description,
            "parameters": request.task_parameters,  # may be legacy; schema normalizes
        },
        "agents": request.agent_definitions,
        "profiles": request.profile_definitions,
    }

    # Validate early for clearer 422 errors (lets schema normalize legacy keys)
    try:
        _ = ConfigSchema(**user_choices)
    except Exception as e:
        http_error(422, "VALIDATION_ERROR", "Invalid configuration fields", {"detail": str(e)})

    # Compute output path (default: <Task>_env.yaml or user-provided filename)
    default_name = f"{_slug(request.task_name)}_env.yaml"
    out_path = _safe_config_path(request.filename or default_name)

    # Delegate to the builder (will re-validate and write YAML)
    builder = ConfigBuilder()
    builder.build_config(user_choices=user_choices, output_path=str(out_path))

    return {"message": "Environment config generated", "path": str(out_path)}

@router.get("/list_configs", response_model=ConfigList, summary="List available scenario configs")
def list_configs():
    files = sorted([f.name for f in CONFIG_DIR.glob("*.y*ml")])
    return {"available_configs": files}

@router.get(
    "/load_config",
    responses={404: {"model": ErrorEnvelope}},
    summary="Load a scenario config YAML by name",
)
def load_config(name: str = Query(..., description="YAML config filename (under haic_env_builder/configs/)")):
    path = _safe_config_path(name)
    if not path.exists():
        http_error(404, "NOT_FOUND", "Config not found", {"name": name})
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        http_error(400, "MALFORMED_YAML", "Unable to parse YAML", {"detail": str(e), "name": name})
    return {"config": data}
