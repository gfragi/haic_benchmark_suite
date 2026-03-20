from __future__ import annotations
from typing import Dict, List, Any, Iterable
import math

def _pctl(xs: List[float], q: float) -> float | None:
    if not xs: return None
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    if lo == hi: return xs[lo]
    f = i - lo
    return xs[lo] * (1 - f) + xs[hi] * f

def _rt_seconds_from_decision(d: Dict[str, Any]) -> float | None:
    # Prefer explicit seconds if present
    v = d.get("duration_s")
    if isinstance(v, (int, float)): return float(v)
    # Fallback to latency_ms -> seconds
    ms = d.get("latency_ms")
    if isinstance(ms, (int, float)): return float(ms) / 1000.0
    return None

def human_response_percentiles_by(
    logs_root: Dict[str, Any],
    group_key: str = "pilot_tag",
    quantiles: Iterable[float] = (0.5, 0.9, 0.95),
) -> Dict[str, Any]:
    """
    Groups human response times (duration_s or latency_ms) by `group_key`.
    Returns Chart.js-friendly payload + human SLA from extras.rt_limits.rt_max_human_s.
    """
    logs = logs_root.get("logs", [])
    by_group: Dict[str, List[float]] = {}

    # Read configured SLA cap — do NOT default to 30; None means unconfigured.
    rt_caps = (logs_root.get("extras", {}) or {}).get("rt_limits", {})
    configured_sla = rt_caps.get("rt_max_human_s")
    try:
        sla_human_s: float | None = float(configured_sla) if configured_sla is not None else None
        sla_source = "configured" if sla_human_s is not None else None
    except (TypeError, ValueError):
        sla_human_s = None
        sla_source = None

    for sess in logs:
        group = str(sess.get(group_key, "unknown"))
        for d in (sess.get("decisions") or []):
            if str(d.get("actor_type", "")).lower() == "human":
                val = _rt_seconds_from_decision(d)
                if val is not None:
                    by_group.setdefault(group, []).append(val)

    # Infer SLA from P95 of all collected human RTs when not configured.
    if sla_human_s is None:
        all_human_rts = [v for vals in by_group.values() for v in vals]
        inferred = _pctl(all_human_rts, 0.95) if all_human_rts else None
        sla_human_s = inferred
        sla_source = "inferred_p95" if inferred is not None else "unavailable"

    labels = sorted(by_group.keys())
    qs = list(quantiles)
    matrix = []
    for q in qs:
        row = []
        for g in labels:
            row.append(_pctl(by_group.get(g, []), q))
        matrix.append(row)

    return {
        "labels": labels,
        "series": [f"p{int(q*100)}" for q in qs],
        "data": matrix,                        # series-major
        "counts": {g: len(xs) for g, xs in by_group.items()},
        "sla_s": sla_human_s,                  # seconds; None when unavailable
        "sla_source": sla_source,              # "configured" | "inferred_p95" | "unavailable"
        "sla_s_inferred": sla_source != "configured",
        "group_key": group_key,
    }
