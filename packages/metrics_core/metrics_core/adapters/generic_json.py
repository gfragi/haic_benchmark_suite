"""
Generic JSON adapter for the standard haic_logging flat-event format.

Field mapping contract (what we expect from haic_logging events):
  agent_id / user_id         → agent
  role / actor_type          → actor_type  (normalised via _ACTOR_MAP)
  action / event_type        → action      (action preferred)
  timestamp                  → timestamp   (s / ms / ns epoch or ISO-8601)
  duration_s                 → duration_s
  response_time_ms / latency_ms → latency_ms
  is_correct                 → correct
  probs                      → probs
  surrogate_probs            → surrogate_probs
  surrogate_action           → surrogate_action
  event_type                 → event_type
  off_role_action            → off_role_action

Nanosecond timestamps are handled by _parse_ts() in models.py.
"""
from __future__ import annotations

from typing import Any, List

from metrics_core.models import DecisionEvent, _parse_ts, _safe_float

# Map raw role / actor_type strings to the canonical three values.
_ACTOR_MAP: dict[str, str] = {
    "human":    "human",
    "operator": "human",
    "user":     "human",
    "pilot":    "human",
    "ai":       "ai",
    "model":    "ai",
    "assistant":"ai",
    "bot":      "ai",
    "system":   "system",
}


def to_decisions(events: List[dict[str, Any]]) -> List[DecisionEvent]:
    """
    Map a list of raw haic_logging event dicts to canonical DecisionEvent records.

    Skips non-dict items silently — malformed events must not abort a run.
    """
    if not events:
        return []

    out: List[DecisionEvent] = []
    for e in events:
        if not isinstance(e, dict):
            continue

        # --- agent identity -------------------------------------------------
        raw_agent = e.get("agent_id") or e.get("user_id") or "unknown"

        # --- actor type -----------------------------------------------------
        raw_role = str(e.get("role") or e.get("actor_type") or "").strip().lower()
        actor_type = _ACTOR_MAP.get(raw_role, raw_role or "unknown")

        # --- action ---------------------------------------------------------
        action = e.get("action") or e.get("event_type") or None

        # --- latency --------------------------------------------------------
        # Prefer response_time_ms (haic_logging name) then latency_ms.
        latency_ms = _safe_float(e.get("response_time_ms") or e.get("latency_ms"))

        # --- probability distributions --------------------------------------
        probs_raw = e.get("probs")
        probs = probs_raw if isinstance(probs_raw, dict) and probs_raw else None

        surrogate_probs_raw = e.get("surrogate_probs")
        surrogate_probs = (
            surrogate_probs_raw
            if isinstance(surrogate_probs_raw, dict) and surrogate_probs_raw
            else None
        )

        out.append(
            DecisionEvent(
                agent=str(raw_agent),
                actor_type=actor_type,
                action=action,
                timestamp=_parse_ts(e.get("timestamp")),
                duration_s=_safe_float(e.get("duration_s")),
                latency_ms=latency_ms,
                correct=e.get("is_correct"),
                probs=probs,
                surrogate_probs=surrogate_probs,
                surrogate_action=e.get("surrogate_action"),
                event_type=e.get("event_type"),
                off_role_action=e.get("off_role_action"),
            )
        )

    return out
