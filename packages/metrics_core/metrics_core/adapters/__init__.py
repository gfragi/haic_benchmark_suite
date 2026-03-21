"""
metrics_core.adapters
---------------------
Adapter modules convert pilot-specific raw event dicts into
canonical DecisionEvent objects.

Available adapters:
  generic_json   — generic haic_logging flat-event format
  pilot_apps     — application-review pilot (application_created /
                   ai_evaluated / operator_verified event types)
"""
from metrics_core.adapters import generic, pilot_apps
from metrics_core.adapters.base import Adapter

__all__ = ["Adapter", "generic", "pilot_apps"]
