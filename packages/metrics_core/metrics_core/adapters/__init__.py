"""
metrics_core.adapters
---------------------
Adapter modules convert pilot-specific raw event dicts into
canonical DecisionEvent objects.

Available adapters:
  generic      — fallback, common alias patterns
  pilot_apps   — application-review pilot (application_created /
                 ai_evaluated / operator_verified event types)
  config_adapter — runtime-registered adapters loaded from
                   adapters/configs/{pilot_tag}.json files
"""
from metrics_core.adapters import generic, pilot_apps, config_adapter
from metrics_core.adapters.base import Adapter

__all__ = ["Adapter", "generic", "pilot_apps", "config_adapter"]
