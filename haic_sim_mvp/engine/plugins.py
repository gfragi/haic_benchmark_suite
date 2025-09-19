# haic_sim_mvp/engine/plugins.py
import importlib
from typing import Any, Dict
from .base import Agent as BaseAgent, Object as BaseObject, Environment as BaseEnv

CLASS_REGISTRY = {
    "base.Agent": BaseAgent,
    "base.Object": BaseObject,
    "base.Environment": BaseEnv,
}

def load_class(path: str):
    if path in CLASS_REGISTRY:
        return CLASS_REGISTRY[path]
    module, cls = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), cls)

def make_agent(spec: Dict[str, Any]) -> BaseAgent:
    cls = load_class(spec.get("class", "base.Agent"))
    if not issubclass(cls, BaseAgent):
        raise TypeError(f"Configured agent class '{cls.__module__}.{cls.__name__}' is not a subclass of Agent")
    return cls(
        entity_id=spec["id"],
        attributes=spec.get("attributes", {}),
        model=spec.get("model"),
        affordances=spec.get("affordances", []),
    )

def make_object(spec: Dict[str, Any]) -> BaseObject:
    cls = load_class(spec.get("class", "base.Object"))
    if not issubclass(cls, BaseObject):
        raise TypeError(f"Configured object class '{cls.__module__}.{cls.__name__}' is not a subclass of Object")
    return cls(
        entity_id=spec["id"],
        attributes=spec.get("attributes", {}),
        affordances=spec.get("affordances", []),
    )

def make_environment(spec: Dict[str, Any]) -> BaseEnv:
    cls = load_class(spec.get("class", "base.Environment"))
    if not issubclass(cls, BaseEnv):
        raise TypeError(f"Configured environment class '{cls.__module__}.{cls.__name__}' is not a subclass of Environment")
    return cls(
        env_id=spec["id"],
        attributes=spec.get("attributes", {}),
    )
