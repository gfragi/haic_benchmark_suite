# haic_env_builder/adapters/registry.py
from __future__ import annotations
from typing import Any, Dict, Type, Union
import importlib

# We store fully-qualified targets and resolve them lazily to avoid circular imports.
# You can also register new adapters at runtime via register_adapter(..).

# canonical map (lowercased keys)
_ADAPTERS: Dict[str, Union[str, Type]] = {
    # CT
    "ct_scan": "haic_env_builder.adapters.ct_scan_adapter:CTScanAdapter",
    # Overcooked
    "overcooked": "haic_env_builder.adapters.overcooked_adapter:OvercookedAdapter",
    # Back-compat alias
    "overcooked_hcai": "haic_env_builder.adapters.overcooked_adapter:OvercookedAdapter",
}

def register_adapter(name: str, target: Union[str, Type]) -> None:
    """
    Register or override an adapter.
      - name: logical environment name (e.g., 'ct_scan', 'overcooked')
      - target: either a type (class) or 'module.path:ClassName' string
    """
    if not name:
        raise ValueError("Adapter name cannot be empty")
    _ADAPTERS[name.lower()] = target

def _resolve(target: Union[str, Type]) -> Type:
    """
    Resolve a 'module:Class' or return the class directly.
    """
    if isinstance(target, str):
        mod_path, sep, cls_name = target.partition(":")
        if not sep:
            raise ValueError(f"Invalid adapter target '{target}' (expected 'module.path:ClassName').")
        module = importlib.import_module(mod_path)
        cls = getattr(module, cls_name, None)
        if cls is None:
            raise ImportError(f"Cannot find class '{cls_name}' in module '{mod_path}'.")
        return cls
    return target  # already a type

def create_adapter(name: str, **env_params: Any):
    """
    Create an adapter instance for the given logical environment name.
    Example:
        adapter = create_adapter('overcooked', layout_name='cramped_room', target_deliveries=2)
    """
    if not name:
        raise ValueError("Adapter name is required")
    key = name.lower()
    target = _ADAPTERS.get(key)
    if target is None:
        # common pitfall: user passed 'adapter' key in config with wrong value
        known = ", ".join(sorted(_ADAPTERS.keys()))
        raise ValueError(f"Unknown adapter '{name}'. Known: {known}")
    cls = _resolve(target)
    return cls(**env_params)
