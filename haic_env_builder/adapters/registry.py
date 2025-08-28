# haic_env_builder/adapters/registry.py
from __future__ import annotations
from typing import Any
from .ct_scan_adapter import CTScanAdapter
from .overcooked_adapter import OvercookedAdapter, MissingDependencyAdapter

def create_adapter(name: str, **kwargs: Any):
    key = (name or "").lower()
    if key in ("ct", "ct_scan", "radiology"):
        return CTScanAdapter(**kwargs)
    if key in ("overcooked", "overcooked_hcai"):

        try:
            return OvercookedAdapter(**kwargs)
        except Exception:
            return MissingDependencyAdapter(**kwargs)
    raise ValueError(f"Unknown environment '{name}'. Known: ct_scan, overcooked")
