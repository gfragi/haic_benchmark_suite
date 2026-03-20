"""
Application-review pilot adapter.

Maps the three canonical event types produced by the applications pilot
to DecisionEvent records.  All other event types are skipped silently so
that future schema additions don't break historical runs.

Event-type contract
-------------------
application_created
    actor_type = human
    Fields used: user_id / applicant_id, timestamp
    No latency, no correctness label (decision not yet made).

ai_evaluated
    actor_type = ai
    Fields used: agent_id / model_id, timestamp,
                 latency_ms / response_time_ms / inference_ms
    correct is absent at this point (ground truth comes later).

operator_verified
    actor_type = human
    Fields used: user_id / operator_id, timestamp,
                 duration_s / handle_time_s,
                 is_correct / correct  (bool or "true"/"false" string)
"""
from __future__ import annotations

from typing import Any, List, Optional

from metrics_core.models import DecisionEvent, _parse_ts, _safe_float

# Event types owned by this pilot schema
_EVENT_ACTOR: dict[str, str] = {
    "application_created": "human",
    "ai_evaluated":        "ai",
    "operator_verified":   "human",
}


def _resolve_correct(e: dict[str, Any]) -> Optional[bool]:
    """
    Extract a boolean correctness label from an operator_verified event.

    Accepts bool, int (1/0), or string ("true"/"false"/"yes"/"no"/"correct"/"incorrect").
    Returns None when the field is absent or unrecognisable.
    """
    raw = e.get("is_correct") if e.get("is_correct") is not None else e.get("correct")
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    # DecisionEvent._coerce_correct will handle string normalisation,
    # but we resolve here so the intent is explicit and testable.
    s = str(raw).strip().lower()
    if s in {"true", "1", "yes", "correct"}:
        return True
    if s in {"false", "0", "no", "incorrect"}:
        return False
    return None


def to_decisions(events: List[dict[str, Any]]) -> List[DecisionEvent]:
    """
    Map application-pilot raw events to canonical DecisionEvent records.

    Skips unrecognised event types and non-dict items without raising.
    """
    if not events:
        return []

    out: List[DecisionEvent] = []
    for e in events:
        if not isinstance(e, dict):
            continue

        et = str(e.get("event_type") or "").strip().lower()
        if et not in _EVENT_ACTOR:
            continue  # unknown event type — skip, don't abort

        actor_type = _EVENT_ACTOR[et]

        if et == "application_created":
            agent = str(e.get("user_id") or e.get("applicant_id") or "applicant")
            out.append(
                DecisionEvent(
                    agent=agent,
                    actor_type="human",
                    action=et,
                    timestamp=_parse_ts(e.get("timestamp")),
                    event_type=et,
                )
            )

        elif et == "ai_evaluated":
            agent = str(e.get("agent_id") or e.get("model_id") or "ai")
            # Accept any of the three latency aliases this pilot emits.
            latency_ms = _safe_float(
                e.get("latency_ms")
                or e.get("response_time_ms")
                or e.get("inference_ms")
            )
            out.append(
                DecisionEvent(
                    agent=agent,
                    actor_type="ai",
                    action=et,
                    timestamp=_parse_ts(e.get("timestamp")),
                    latency_ms=latency_ms,
                    event_type=et,
                )
            )

        elif et == "operator_verified":
            agent = str(e.get("user_id") or e.get("operator_id") or "operator")
            # Accept either duration_s or handle_time_s as the human RT field.
            duration_s = _safe_float(
                e.get("duration_s") or e.get("handle_time_s")
            )
            out.append(
                DecisionEvent(
                    agent=agent,
                    actor_type="human",
                    action=et,
                    timestamp=_parse_ts(e.get("timestamp")),
                    duration_s=duration_s,
                    correct=_resolve_correct(e),
                    event_type=et,
                )
            )

    return out
