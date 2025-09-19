from __future__ import annotations
from typing import Dict, Any, List, Optional
import importlib, os, math



# ---------- flexible loader ----------
def _resolve_metrics():
    candidates = [
        os.getenv("HAIC_METRICS_MODULE"),
        "metrics_core.interaction_metrics",
        "interaction_metrics",
    ]
    errors = []
    for mod in candidates:
        if not mod:
            continue
        try:
            m = importlib.import_module(mod)
            cm = getattr(m, "compute_metrics")
            cmba = getattr(m, "compute_metrics_by_agent")
            return cm, cmba, mod
        except Exception as e:
            errors.append(f"{mod}: {e}")
    return None, None, None

_CM, _CM_BY, _CM_MODULE = _resolve_metrics()

# ---------- sanitize + mapping ----------
def _to_float_or_none(x):
    try: return float(x)
    except Exception: return None

def _to_interaction_rows(log: Dict[str, Any]) -> List[Dict[str, Any]]:
    decisions = log.get("decisions", [])
    agents_meta: Dict[str, Any] = log.get("agents", {})
    rows: List[Dict[str, Any]] = []
    for d in decisions:
        agent_id = d.get("agent_id") or d.get("agent")
        effect = d.get("effect") or {}
        meta = agents_meta.get(agent_id, {})
        lat_ms = _to_float_or_none(d.get("latency_ms"))
        dur_s = _to_float_or_none(d.get("duration_s"))
        if dur_s is None and lat_ms is not None:
            dur_s = max(0.0, lat_ms / 1000.0)
        if dur_s is None: dur_s = 0.0
        if lat_ms is None: lat_ms = dur_s * 1000.0
        rows.append({
            "t": d.get("t"),
            "agent": agent_id,
            "action": d.get("action"),
            "duration_s": dur_s,
            "latency_ms": lat_ms,
            "actor_type": meta.get("model"),
            "correct": d.get("correct"),
            "probs": effect.get("probs"),
            "surrogate_probs": effect.get("surrogate_probs"),
            "surrogate_action": effect.get("surrogate_action"),
            "event_type": d.get("event_type"),
            "off_role_action": effect.get("off_role_action"),
        })
    return rows

def haic_metrics_for_log(log: Dict[str, Any], *, baseline_s: Optional[float] = None, rt_max: float = 5.0, T: Optional[float] = None) -> Dict[str, float]:
    if _CM is None:  # keep app running even if not installed
        return {}
    env_attrs = (log.get("attributes") or {})
    if baseline_s is None:
        baseline_s = env_attrs.get("baseline_s")
    if rt_max is None:
        rt_max = env_attrs.get("rt_max", 5.0)
    return _CM(decisions=_to_interaction_rows(log), T=T, baseline_s=baseline_s, rt_max=rt_max)

def haic_metrics_by_agent_for_log(log: Dict[str, Any], *, baseline_s: Optional[float] = None, rt_max: float = 5.0, T: Optional[float] = None) -> Dict[str, Dict[str, float]]:
    if _CM_BY is None:
        return {}
    return _CM_BY(decisions=_to_interaction_rows(log), T=T, baseline_s=baseline_s, rt_max=rt_max)
