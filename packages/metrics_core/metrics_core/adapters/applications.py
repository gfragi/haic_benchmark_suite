"""
Adapter registry — maps pilot_tag to a field mapping adapter.
Each adapter converts raw pilot data into DecisionEvent-compatible dicts.
Add one entry per pilot. Falls back to generic adapter if tag not registered.
"""
from __future__ import annotations
from typing import Any


class AdapterRegistry:
    _adapters: dict[str, callable] = {}

    @classmethod
    def register(cls, pilot_tag: str):
        """Decorator: @AdapterRegistry.register('applications')"""
        def decorator(fn):
            cls._adapters[pilot_tag.lower()] = fn
            return fn
        return decorator

    @classmethod
    def adapt(cls, pilot_tag: str, sessions: list[dict]) -> list[dict]:
        """
        Run the adapter for this pilot_tag.
        Returns sessions with fields normalized to DecisionEvent names.
        Falls back to generic (pass-through) if no adapter registered.
        """
        tag = (pilot_tag or "").lower()
        fn = cls._adapters.get(tag) or cls._adapters.get("generic")
        if fn is None:
            return sessions  # bare pass-through
        return fn(sessions)