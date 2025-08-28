# haic_env_builder/components/agent.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence

class Agent:
    """
    Minimal, schema-tolerant agent.
    Accepts optional runtime/runtime_params for policies and ignores unknown fields (stored in .extra).
    """

    def __init__(
        self,
        name: str,
        modality: str = "policy",
        capabilities: Optional[Sequence[str]] = None,
        # runtime bits are optional
        runtime: Optional[str] = None,
        runtime_params: Optional[Dict[str, Any]] = None,
        # optional declared actor type, if you want to tag human vs ai at config level
        actor_type: Optional[str] = None,
        **kwargs: Any,  # swallow unknown keys to keep configs flexible
    ) -> None:
        self.name: str = name
        self.modality: str = modality or "policy"
        self.capabilities: List[str] = list(capabilities) if capabilities else []
        self.runtime: Optional[str] = runtime
        self.runtime_params: Dict[str, Any] = dict(runtime_params) if runtime_params else {}
        self.actor_type: Optional[str] = actor_type

        # keep any extra fields for debugging / future use; never break on them
        self.extra: Dict[str, Any] = dict(kwargs)

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, modality={self.modality!r}, runtime={self.runtime!r})"

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "name": self.name,
            "modality": self.modality,
            "capabilities": self.capabilities or [],
        }
        if self.runtime is not None:
            out["runtime"] = self.runtime
        if self.runtime_params:
            out["runtime_params"] = self.runtime_params
        if self.actor_type:
            out["actor_type"] = self.actor_type
        if self.extra:
            out["extra"] = self.extra
        return out
