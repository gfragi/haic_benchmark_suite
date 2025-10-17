from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional

# sim decisions/events are pydantic models; accept either dicts or model instances
def _get(d: Any, key: str, default=None):
    if isinstance(d, dict):
        return d.get(key, default)
    return getattr(d, key, default)

def export_collab_decisions(
    *,
    sim_decisions: Iterable[Any],
    # Optional enrichments / defaults if the sim log lacks these:
    default_actor_type: Optional[str] = "ai",
    default_duration_s: Optional[float] = None,
    default_latency_ms: Optional[float] = None,
    outcome_fn=None,   # function(decision)->Optional[bool] to compute 'correct'
    probs_fn=None,     # function(decision)->Optional[Dict[str,float]]
    surrogate_fn=None, # function(decision)->(surrogate_probs or action)
) -> List[Dict[str, Any]]:
    """
    Map haic_env_builder.schemas.decision.Decision -> collab API decision dict.
    """
    out: List[Dict[str, Any]] = []
    for d in sim_decisions:
        t = float(_get(d, "t", 0))
        agent = _get(d, "agent_id") or _get(d, "agent")  # sim uses agent_id
        action = _get(d, "action")
        actor_type = default_actor_type
        duration_s = default_duration_s
        latency_ms = default_latency_ms
        correct = outcome_fn(d) if outcome_fn else None
        probs = probs_fn(d) if probs_fn else None

        s_probs = None
        s_action = None
        if surrogate_fn:
            s_val = surrogate_fn(d)
            if isinstance(s_val, dict):
                s_probs = s_val
            else:
                s_action = s_val

        out.append({
            "t": t,
            "agent": agent,
            "actor_type": actor_type,
            "action": action,
            "duration_s": duration_s,
            "latency_ms": latency_ms,
            "correct": correct,
            "probs": probs,
            "surrogate_probs": s_probs,
            "surrogate_action": s_action,
            #  can also pass 'event_type' if you derive it:
            # "event_type": "error" if ... else None,
        })
    return out
