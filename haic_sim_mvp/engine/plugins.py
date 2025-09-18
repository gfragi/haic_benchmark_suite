
import importlib
from typing import Any, Dict
from .base import Agent, Object, Environment

CLASS_REGISTRY = {"base.Agent": Agent, "base.Object": Object, "base.Environment": Environment}

def load_class(path: str):
    if path in CLASS_REGISTRY: return CLASS_REGISTRY[path]
    module, cls = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), cls)

def make_agent(spec: Dict[str, Any]) -> Agent:
    cls = load_class(spec.get("class", "base.Agent"))
    return cls(entity_id=spec["id"], attributes=spec.get("attributes", {}), model=spec.get("model"), affordances=spec.get("affordances", []))

def make_object(spec: Dict[str, Any]) -> Object:
    cls = load_class(spec.get("class", "base.Object"))
    return cls(entity_id=spec["id"], attributes=spec.get("attributes", {}), affordances=spec.get("affordances", []))

def make_environment(spec: Dict[str, Any]) -> Environment:
    cls = load_class(spec.get("class", "base.Environment"))
    return cls(env_id=spec["id"], attributes=spec.get("attributes", {}))
