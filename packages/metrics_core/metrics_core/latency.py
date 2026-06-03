from __future__ import annotations
from typing import Dict, List, Any, Iterable, Tuple
import math

def _pctl(xs: List[float], q: float) -> float | None:
    if not xs: return None
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    if lo == hi: return xs[lo]
    f = i - lo
    return xs[lo] * (1 - f) + xs[hi] * f

def _latency_ms_from_decision(d: Dict[str, Any]) -> float | None:
    """
    Extract AI latency in milliseconds from a decision dict.

    Field priority:
      latency_ms   — already in ms; use directly.
      duration_s   — name says seconds; convert × 1000.
      latency      — no unit in the field name; skip rather than guess.
                     A 400 ms response would be misclassified as 400 s
                     by any threshold heuristic, so we drop ambiguous fields.
    """
    v = d.get("latency_ms")
    if isinstance(v, (int, float)):
        return float(v)
    s = d.get("duration_s")
    if isinstance(s, (int, float)):
        return 1000.0 * float(s)
    # bare "latency" field has no unit — do not guess
    return None

def latency_percentiles_by(
    logs_root: Dict[str, Any],
    group_key: str = "ai_model_version",
    quantiles: Iterable[float] = (0.5, 0.9, 0.95),
) -> Dict[str, Any]:
    """
    Accepts a HAIC log root with {"logs":[{session...}]}
    Groups latencies from ai_evaluated decisions by `group_key` (default: ai_model_version).
    Returns Chart.js-friendly payload + SLA caps (if present).
    """
    logs = logs_root.get("logs", [])
    by_group: Dict[str, List[float]] = {}

    # read SLA caps if present
    rt_caps = (logs_root.get("extras", {}) or {}).get("rt_limits", {})
    sla_ai_ms = float(rt_caps.get("rt_max_ai_ms", 5000))

    for sess in logs:
        group = str(sess.get(group_key, "unknown"))
        for d in sess.get("decisions", []) or []:
            actor = str(d.get("actor_type") or "").strip().lower()
            action = str(d.get("action") or "").strip().lower()
            # Primary: actor_type == "ai" (set by adapters).
            # Fallback: hardcoded action names for logs that lack actor_type.
            is_ai = (
                actor == "ai"
                or (not actor and action in {"ai_evaluated", "classify", "forecast"})
            )
            if not is_ai:
                continue
            v = _latency_ms_from_decision(d)
            if v is not None:
                by_group.setdefault(group, []).append(v)

    labels = sorted(by_group.keys())
    q_list = list(quantiles)
    matrix = []
    for q in q_list:
        row = []
        for g in labels:
            row.append(_pctl(by_group.get(g, []), q))
        matrix.append(row)

    return {
        "labels": labels,                # x-axis: groups (models)
        "series": [f"p{int(q*100)}" for q in q_list],
        "data": matrix,                  # series-major: data[i_series][i_label]
        "counts": {g: len(xs) for g, xs in by_group.items()},
        "sla_ms": sla_ai_ms,
        "group_key": group_key,
    }
