"""
Generic adapter — fallback for unregistered pilot_tags.
Attempts best-effort field mapping using common alias patterns.
Produces warnings for fields it cannot resolve.
"""
from __future__ import annotations
from .registry import AdapterRegistry

# Common field name aliases across pilot types
_FIELD_ALIASES = {
    "actor_type":  ["actor_type", "role", "actor", "agent_type", "user_type"],
    "action":      ["action", "event_type", "type", "event_name", "action_type"],
    "latency_ms":  ["latency_ms", "inference_ms", "response_time_ms",
                    "control_latency_ms", "ai_latency_ms"],
    "duration_s":  ["duration_s", "review_time_s", "decision_time_s",
                    "handling_time_s", "operator_time_s"],
    "correct":     ["correct", "is_correct", "agreement", "confirmed",
                    "resolved", "target_met", "radiologist_agrees",
                    "grid_stable", "customer_satisfied"],
    "timestamp":   ["timestamp", "time", "created_at", "event_time",
                    "ts", "datetime", "occurred_at"],
    "interaction_id": ["interaction_id", "case_id", "ticket_id",
                       "session_id", "event_id", "record_id"],
}

_ACTOR_TYPE_MAP = {
    "human": "human", "operator": "human", "radiologist": "human",
    "citizen": "human", "agent": "human", "user": "human",
    "ai": "ai", "model": "ai", "classifier": "ai", "system": "ai",
    "controller": "ai", "bot": "ai",
}


def _pick(d: dict, aliases: list[str]):
    for k in aliases:
        if k in d and d[k] not in (None, "", [], {}):
            return d[k]
    return None


@AdapterRegistry.register("generic")
def adapt_generic(sessions: list[dict]) -> list[dict]:
    adapted = []
    for session in sessions:
        decisions = session.get("decisions") or []
        new_decisions = []

        for d in decisions:
            nd = dict(d)

            # Normalize actor_type
            if "actor_type" not in nd or nd["actor_type"] is None:
                raw = _pick(nd, _FIELD_ALIASES["actor_type"])
                if raw is not None:
                    nd["actor_type"] = _ACTOR_TYPE_MAP.get(
                        str(raw).lower(), str(raw).lower()
                    )

            # Normalize timing fields
            for field, aliases in [
                ("latency_ms", _FIELD_ALIASES["latency_ms"]),
                ("duration_s",  _FIELD_ALIASES["duration_s"]),
                ("correct",     _FIELD_ALIASES["correct"]),
                ("timestamp",   _FIELD_ALIASES["timestamp"]),
                ("interaction_id", _FIELD_ALIASES["interaction_id"]),
            ]:
                if field not in nd or nd[field] is None:
                    val = _pick(nd, aliases)
                    if val is not None:
                        nd[field] = val

            # Convert boolean-like strings for 'correct'
            if isinstance(nd.get("correct"), str):
                nd["correct"] = nd["correct"].lower() in {
                    "true", "yes", "1", "correct", "resolved",
                    "accepted", "confirmed", "stable"
                }

            new_decisions.append(nd)

        adapted.append({**session, "decisions": new_decisions})

    return adapted