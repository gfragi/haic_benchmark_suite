from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from pathlib import Path
import re
import yaml
import json

from app.models.api import ConfigList, MessageWithPath, ErrorEnvelope
from app.utils.errors import http_error
from haic_env_builder.config_builder.builder import ConfigBuilder
from haic_env_builder.schemas.config import ConfigSchema  # validate early for clear 422s

router = APIRouter()

# ---------- project root detection ----------
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    # First check for Docker container structure: /app with haic_env_builder and haic_sim_mvp
    app_root = Path("/app")
    if app_root.exists() and (app_root / "haic_env_builder").is_dir() and (app_root / "haic_sim_mvp").is_dir():
        return app_root

    # Fallback to original logic for local development
    for cand in [*here.parents]:
        if (cand / "backend").is_dir() and (cand / "haic_env_builder").is_dir():
            return cand
    # fallback: go up 3 if structure is standard: repo/backend/app/routers/...
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]

PROJECT_ROOT = _find_project_root()
HAIC_DIR = PROJECT_ROOT / "haic_env_builder" / "configs"
HAIC_SIM_DIR = PROJECT_ROOT / "haic_sim_mvp" / "configs"
LEGACY_DIR = PROJECT_ROOT / "configs"
CONFIG_DIRS = [HAIC_DIR, HAIC_SIM_DIR, LEGACY_DIR]
DEFAULT_WRITE_DIR = HAIC_SIM_DIR
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

# ---------- HAIC Sim MVP routes ----------
HAIC_SIM_MVP_DIR = PROJECT_ROOT / "haic_sim_mvp"
HAIC_CONFIGS_DIR = HAIC_SIM_MVP_DIR / "configs"
HAIC_EXAMPLES_DIR = HAIC_SIM_MVP_DIR / "examples"
HAIC_ADAPTERS_DIR = PROJECT_ROOT / "haic_env_builder" / "adapters"
HAIC_PLUGINS_DIR = HAIC_SIM_MVP_DIR / "user_plugins"

@router.get("/haic_configs", summary="List available HAIC Sim MVP configuration files")
def list_haic_configs():
    configs = []

    # Only return configs, not examples
    if HAIC_CONFIGS_DIR.exists():
        for f in HAIC_CONFIGS_DIR.glob("*.json"):
            configs.append({
                "name": f.name,
                "path": str(f.relative_to(PROJECT_ROOT)),
                "type": "config"
            })

    return {
        "configs": sorted(configs, key=lambda x: x["name"]),
        "examples": []  # Keep empty for backward compatibility
    }

@router.get("/haic_pilot_configs", summary="List available HAIC Sim MVP pilot configurations for Environment Builder")
def list_haic_pilot_configs():
    pilots = []

    if HAIC_CONFIGS_DIR.exists():
        for f in HAIC_CONFIGS_DIR.glob("*.json"):
            if f.name != "MANIFEST.in":  # Skip non-config files
                try:
                    with open(f, "r") as file:
                        config = json.load(file)
                        domain = config.get("environment", {}).get("attributes", {}).get("domain", "general")
                        task = config.get("environment", {}).get("attributes", {}).get("task", "task")

                        pilots.append({
                            "name": f.name.replace(".json", ""),
                            "display_name": f"{domain.title()} {task.replace('_', ' ').title()}",
                            "domain": domain,
                            "task": task,
                            "sim_id": config.get("sim_id", ""),
                            "filename": f.name
                        })
                except Exception as e:
                    print(f"Warning: Could not parse {f.name}: {e}")

    return {"pilots": sorted(pilots, key=lambda x: x["name"])}

@router.get("/haic_pilot_config", summary="Load and convert a HAIC Sim MVP pilot config to Environment Builder format")
def load_haic_pilot_config(name: str = Query(..., description="Config filename (without .json extension)")):
    # Search in configs directory
    if HAIC_CONFIGS_DIR.exists():
        config_file = HAIC_CONFIGS_DIR / f"{name}.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    haic_config = json.load(f)

                # Convert HAIC config to Environment Builder format
                env_builder_config = convert_haic_to_env_builder(haic_config)

                return {"config": env_builder_config, "original_haic_config": haic_config}
            except Exception as e:
                http_error(400, "CONVERSION_ERROR", f"Failed to convert HAIC config: {e}", {"name": name})

    http_error(404, "NOT_FOUND", "HAIC pilot config not found", {"name": name})

def convert_haic_to_env_builder(haic_config):
    """Convert HAIC Sim MVP config to Environment Builder format"""

    # Extract environment info
    env_info = haic_config.get("environment", {})
    domain = env_info.get("attributes", {}).get("domain", "general")
    task = env_info.get("attributes", {}).get("task", "task")

    # Convert agents
    agents = []
    for agent in haic_config.get("agents", []):
        agent_type = "ai" if agent.get("model") == "ai" else "human"
        # Get affordances from the agent
        affordances = agent.get("affordances", [])
        if isinstance(affordances, list):
            affordances_str = ",".join(affordances)
        else:
            affordances_str = str(affordances)

        agents.append({
            "id": agent["id"],
            "type": agent_type,
            "profile": agent.get("class", "default").split(".")[-1],
            "affordances": affordances_str
        })

    # Convert objects
    objects = []
    for obj in haic_config.get("objects", []):
        # Get affordances from the object
        affordances = obj.get("affordances", [])
        if isinstance(affordances, list):
            affordances_str = ",".join(affordances)
        else:
            affordances_str = str(affordances)

        objects.append({
            "id": obj["id"],
            "class": obj.get("class", "base.Object"),
            "kind": obj.get("attributes", {}).get("kind", obj.get("kind", "resource")),
            "affordances": affordances_str
        })

    # Convert script to Environment Builder format
    script = []
    for i, step in enumerate(haic_config.get("script", [])):
        script_step = {
            "t": step.get("t", i + 1),
            "agent": step.get("agent", ""),
            "action": step.get("action", ""),
            "object": step.get("object", ""),
            "effect_json": json.dumps(step.get("effect", {"result": "value"})) if isinstance(step.get("effect"), dict) else step.get("effect_json", '{"result":"value"}'),
            "latency_ms": step.get("latency_ms", 1000),
            "correct": step.get("correct", True)
        }
        script.append(script_step)

    # Group script actions into tasks (simplified approach)
    tasks = []

    # Create a single task from the script sequence
    actions = []
    for i, step in enumerate(haic_config.get("script", [])):
        action = {
            "id": f"action_{i}",
            "name": step.get("action", f"Action {i+1}"),
            "actor": step.get("agent", ""),
            "duration_s": step.get("duration_s", 1.0),
            "latency_ms": step.get("latency_ms"),
            "correct": step.get("correct", True)
        }
        actions.append(action)

    if actions:
        tasks.append({
            "id": f"{domain}_task",
            "name": f"{domain.title()} {task.title()} Task",
            "actions": actions
        })

    # Set appropriate metrics based on domain
    metrics = { "rt_max": 5.0, "baseline_s": None }
    if domain == "manufacturing":
        metrics = { "rt_max": 3.0, "baseline_s": 1.5 }
    elif domain == "medical":
        metrics = { "rt_max": 5.0, "baseline_s": 2.0 }

    return {
        "name": f"{domain.title()} Environment ({haic_config.get('sim_id', 'converted')})",
        "version": "v1",
        "metrics": metrics,
        "agents": agents,
        "objects": objects,
        "tasks": tasks,
        "script": script
    }

@router.get("/haic_config", summary="Load a HAIC Sim MVP config by name")
def load_haic_config(name: str = Query(..., description="Config filename (without .json extension)")):
    # Search in configs first, then examples
    search_dirs = [HAIC_CONFIGS_DIR, HAIC_EXAMPLES_DIR]

    for base_dir in search_dirs:
        if base_dir.exists():
            config_file = base_dir / f"{name}.json"
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        data = json.load(f)
                    return {"config": data, "path": str(config_file.relative_to(PROJECT_ROOT))}
                except Exception as e:
                    http_error(400, "MALFORMED_JSON", f"Unable to parse JSON: {e}", {"name": name})

    http_error(404, "NOT_FOUND", "HAIC config not found", {"name": name})

@router.get("/haic_adapters", summary="List available HAIC adapters")
def list_haic_adapters():
    adapters = []
    if HAIC_ADAPTERS_DIR.exists():
        for f in HAIC_ADAPTERS_DIR.glob("*.py"):
            if not f.name.startswith("__"):
                adapters.append({
                    "name": f.stem,
                    "path": str(f.relative_to(PROJECT_ROOT))
                })
    return {"adapters": sorted(adapters, key=lambda x: x["name"])}

@router.get("/haic_plugins", summary="List available HAIC user plugins")
def list_haic_plugins():
    plugins = []
    if HAIC_PLUGINS_DIR.exists():
        for f in HAIC_PLUGINS_DIR.glob("*.py"):
            if not f.name.startswith("__"):
                plugins.append({
                    "name": f.stem,
                    "path": str(f.relative_to(PROJECT_ROOT))
                })
    return {"plugins": sorted(plugins, key=lambda x: x["name"])}
