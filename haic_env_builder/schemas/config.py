# haic_env_builder/schemas/config.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# -----------------
# Coercion helpers
# -----------------
def _coerce_scalar(v: Any) -> Any:
    if isinstance(v, str):
        s = v.strip()
        low = s.lower()
        if low in {"true", "false"}:
            return low == "true"
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            return v
    return v

def _coerce_dict(d: Dict[str, Any] | None) -> Dict[str, Any]:
    if not isinstance(d, dict):
        return {}
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = _coerce_dict(v)
        elif isinstance(v, list):
            out[k] = [_coerce_scalar(x) for x in v]
        else:
            out[k] = _coerce_scalar(v)
    return out

# -----------------
# Task parameters
# -----------------
class TaskParams(BaseModel):
    """
    Canonical task parameters for the adapter-driven runner.
    - environment: short name of the adapter (e.g., "ct_scan", "overcooked")
    - env_params: passed directly to the adapter ctor
    - dt: optional core tick used if adapter doesn't emit 't'
    - baseline_s / rt_max: optional core metric knobs
    """
    model_config = ConfigDict(extra="allow")

    environment: str = Field(default="ct_scan")
    env_params: Dict[str, Any] = Field(default_factory=dict)
    dt: float = 0.1
    baseline_s: Optional[float] = None
    rt_max: Optional[float] = 5.0

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy(cls, v: Any) -> Any:
        """
        Accept legacy shapes and normalize to:
          { environment, env_params, dt, baseline_s?, rt_max? }
        Legacy keys:
          - adapter: "overcooked_hcai" -> environment="overcooked"
          - layout_name / horizon_s / steps / dt at top-level
        """
        if not isinstance(v, dict):
            return v
        raw = dict(v)

        env = raw.get("environment") or raw.get("adapter")
        if env == "overcooked_hcai":
            env = "overcooked"

        # Infer if missing
        if not env:
            if any(k in raw for k in ("layout_name", "horizon_s")):
                env = "overcooked"
            elif any(k in raw for k in ("steps", "dt")):
                env = "ct_scan"
            else:
                env = "ct_scan"  # safe default

        env_params = dict(raw.get("env_params", {}) or {})

        # Move known per-env knobs into env_params (non-destructive)
        if env == "overcooked":
            for k in ("layout_name", "horizon_s", "dt"):
                if k in raw and k not in env_params:
                    env_params[k] = raw[k]
        elif env == "ct_scan":
            for k in ("steps", "dt"):
                if k in raw and k not in env_params:
                    env_params[k] = raw[k]

        dt = raw.get("dt", env_params.get("dt", 0.1))

        out = {
            "environment": env,
            "env_params": env_params,
            "dt": float(dt),
        }
        # pass through core metric controls if present
        for k in ("baseline_s", "rt_max"):
            if k in raw:
                out[k] = _coerce_scalar(raw[k])

        # Keep any other extra keys for forward-compat
        for k, v2 in raw.items():
            if k not in out and k not in {"adapter", "layout_name", "horizon_s", "steps"}:
                out[k] = v2
        return out

    @field_validator("env_params", mode="before")
    @classmethod
    def coerce_env_params(cls, v: Any) -> Dict[str, Any]:
        return _coerce_dict(v)

# -----------------
# Task
# -----------------
class TaskSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None
    parameters: TaskParams

# -----------------
# Agent
# -----------------
class AgentSchema(BaseModel):
    """
    Flexible agent schema:
    - 'modality' is a free string (e.g., "policy", "text", "audio", "visual", "human")
    - optional 'runtime' / 'runtime_params' for policy backends
    - optional 'action_space' to pin allowed actions (adapter may still clamp)
    """
    model_config = ConfigDict(extra="allow")

    name: str
    modality: str = "policy"
    capabilities: List[str] = Field(default_factory=list)
    runtime: Optional[str] = None
    runtime_params: Dict[str, Any] = Field(default_factory=dict)
    actor_type: Optional[str] = None  # e.g., "ai" | "human"
    action_space: Optional[List[str]] = None

    @field_validator("capabilities", mode="before")
    @classmethod
    def coerce_capabilities(cls, v: Any) -> List[str]:
        if v is None:
            return []
        return list(v)

    @field_validator("runtime_params", mode="before")
    @classmethod
    def coerce_runtime_params(cls, v: Any) -> Dict[str, Any]:
        return _coerce_dict(v)

# -----------------
# Profile
# -----------------
class ProfileSchema(BaseModel):
    """
    Accepts either 'id' or 'profile_id' on input; exposed as 'profile_id'.
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    profile_id: str = Field(alias="id")
    role: Optional[str] = None
    skill_level: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def accept_profile_id_or_id(cls, v: Any) -> Any:
        if isinstance(v, dict):
            if "profile_id" in v and "id" not in v:
                v = dict(v)
                v["id"] = v.pop("profile_id")
        return v

    @field_validator("metadata", mode="before")
    @classmethod
    def coerce_metadata(cls, v: Any) -> Dict[str, Any]:
        return _coerce_dict(v)

# -----------------
# Top-level Config
# -----------------
class ConfigSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    task: TaskSchema
    agents: List[AgentSchema]
    profiles: List[ProfileSchema] = Field(default_factory=list)
