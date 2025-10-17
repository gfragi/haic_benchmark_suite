# haic_env_builder/components/task.py
from __future__ import annotations
from typing import Any, Dict, Optional
from .base import Component

class Task(Component):
    """
    Minimal, schema-tolerant Task.
    - 'description' is optional
    - swallows unknown keys into .extra
    - tiny helpers to read environment params without leaking adapter details into the core
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,  # swallow unknown keys from YAML
    ):
        self.name = name
        self.description = description
        self.parameters: Dict[str, Any] = dict(parameters) if parameters else {}
        self.extra: Dict[str, Any] = dict(kwargs)

    # ---- tiny helpers used by runner/config builder ----
    def environment(self) -> Optional[str]:
        # prefer 'environment', but allow legacy 'adapter'
        p = self.parameters or {}
        return p.get("environment") or p.get("adapter")

    def env_params(self) -> Dict[str, Any]:
        return (self.parameters or {}).get("env_params", {}) or {}

    def dt(self, default: float = 0.1) -> float:
        try:
            return float((self.parameters or {}).get("dt", default))
        except Exception:
            return float(default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            **({"extra": self.extra} if self.extra else {}),
        }
