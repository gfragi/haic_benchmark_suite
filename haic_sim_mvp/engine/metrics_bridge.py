# engine/metrics_bridge.py
from __future__ import annotations
from typing import Dict, Any, List, Optional

try:
    from metrics_core.interaction_metrics import compute_metrics as compute_haic_metrics
    from metrics_core.interaction_metrics import compute_metrics_by_agent as compute_haic_metrics_by_agent
except ImportError as e:
    raise ImportError(
        "interaction_metrics not found. Install your root project that contains "
        "interaction_metrics.py (e.g., `pip install -e .`) or fix PYTHONPATH."
    ) from e

def _to_float_or_none(x):
    try:
        return float(x)
    except Exception:
        return None

def _to_interaction_rows(log: Dict[str, Any]) -> List[Dict[str, Any]]:
    decisions = log.get("decisions", [])
    agents_meta: Dict[str, Any] = log.get("agents", {})

    rows: List[Dict[str, Any]] = []
    for d in decisions:
        agent_id = d.get("agent_id") or d.get("agent")
        meta = agents_meta.get(agent_id, {})
        actor_type = meta.get("model")  # "human" / "ai" / "surrogate" etc.

        effect = d.get("effect", {}) or {}

        # --- sanitize timing fields ---
        lat_ms_raw = d.get("latency_ms", None)
        lat_ms = _to_float_or_none(lat_ms_raw)
        dur_s_raw = d.get("duration_s", None)
        dur_s = _to_float_or_none(dur_s_raw)

        # Prefer duration_s; otherwise derive from latency_ms
        if dur_s is None and lat_ms is not None:
            dur_s = max(0.0, lat_ms / 1000.0)

        # Ensure we NEVER pass None for both; fall back to 0.0
        if dur_s is None and lat_ms is None:
            dur_s = 0.0
            lat_ms = 0.0

        row = {
            "t": d.get("t"),
            "agent": agent_id,
            "action": d.get("action"),
            "duration_s": dur_s,            # guaranteed number
            "latency_ms": lat_ms,           # guaranteed number
            "actor_type": actor_type,
            "correct": d.get("correct"),

            # Optional similarity / events
            "probs": effect.get("probs"),
            "surrogate_probs": effect.get("surrogate_probs"),
            "surrogate_action": effect.get("surrogate_action"),
            "event_type": d.get("event_type"),
            "off_role_action": effect.get("off_role_action"),
        }
        rows.append(row)
    return rows

def haic_metrics_for_log(log: Dict[str, Any], *, baseline_s: Optional[float] = None, rt_max: float = 5.0, T: Optional[float] = None) -> Dict[str, float]:
    rows = _to_interaction_rows(log)
    env_attrs = (log.get("attributes") or {})
    if baseline_s is None:
        baseline_s = env_attrs.get("baseline_s", None)
    if rt_max is None:
        rt_max = env_attrs.get("rt_max", 5.0)
    return compute_haic_metrics(decisions=rows, T=T, baseline_s=baseline_s, rt_max=rt_max)

def haic_metrics_by_agent_for_log(log: Dict[str, Any], *, baseline_s: Optional[float] = None, rt_max: float = 5.0, T: Optional[float] = None) -> Dict[str, Dict[str, float]]:
    rows = _to_interaction_rows(log)
    return compute_haic_metrics_by_agent(decisions=rows, T=T, baseline_s=baseline_s, rt_max=rt_max)
