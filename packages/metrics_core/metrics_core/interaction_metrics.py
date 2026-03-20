"""
interaction_metrics — collab-session metric computation.

Responsibility split:
  Adapters      → field mapping  (pilot aliases → canonical names)
  This module   → t derivation, math, aggregation

_normalize_decisions() no longer does alias resolution.  It only:
  1. Converts DecisionEvent objects to dicts via model_dump().
  2. Parses raw timestamp strings/ints to datetime (dict-path compat).
  3. Derives the numeric `t` field from timestamps or a monotonic counter.

compute_metrics() and compute_metrics_by_agent() accept either
List[DecisionEvent] (adapter output) or List[dict] (backward-compat).
"""
from __future__ import annotations

import math
import datetime as dt
from typing import Any, Callable, Dict, List, Optional, Union

from metrics_core.models import DecisionEvent, _parse_ts, _safe_float

DEFAULT_RT_MAX: float = 5.0   # seconds
DEFAULT_BASELINE_S: Optional[float] = None

# Soft weights for composite EfficiencyScore shaping
_OFFROLE_PENALTY_WEIGHT: float = 0.35
_PROGRESS_BONUS_WEIGHT: float = 0.10

# Type alias accepted by the public API
_DecisionInput = Union[Dict[str, Any], DecisionEvent]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sec(a: dt.datetime, b: dt.datetime) -> float:
    """Signed elapsed seconds from a to b."""
    return (b - a).total_seconds()


def _normalize_decisions(
    decisions: List[_DecisionInput],
) -> List[Dict[str, Any]]:
    """
    Accepts DecisionEvent objects or plain dicts with canonical field names.

    For DecisionEvent inputs: model_dump() → dict with typed fields.
    For dict inputs: shallow-copy, parse timestamp string → datetime if needed.

    In both cases: derive numeric `t` from `timestamp` when absent,
    falling back to a monotonic counter (1-second increments).

    Alias resolution is NOT done here — that is the adapter's responsibility.
    """
    if not decisions:
        return []

    norm_rows: List[Dict[str, Any]] = []
    all_ts: List[dt.datetime] = []

    for e in decisions:
        if isinstance(e, DecisionEvent):
            row = e.model_dump()
        elif isinstance(e, dict):
            row = dict(e)
        else:
            continue

        # Ensure timestamp is a tz-aware datetime object (or None)
        ts_raw = row.get("timestamp")
        if isinstance(ts_raw, dt.datetime):
            ts_dt: Optional[dt.datetime] = (
                ts_raw if ts_raw.tzinfo else ts_raw.replace(tzinfo=dt.timezone.utc)
            )
        else:
            ts_dt = _parse_ts(ts_raw)

        if ts_dt is not None:
            all_ts.append(ts_dt)
            row["timestamp"] = ts_dt  # normalise: always datetime after this point

        if "t" not in row or row["t"] is None:
            row["t"] = None  # filled in the second pass below

        norm_rows.append(row)

    # Derive t from timestamps (or monotonic counter when timestamps absent)
    s_start = min(all_ts) if all_ts else None
    monotonic = 0.0
    for r in norm_rows:
        if r.get("t") is None:
            ts_dt = r.get("timestamp")
            if s_start is not None and isinstance(ts_dt, dt.datetime):
                r["t"] = max(0.0, _sec(s_start, ts_dt))
            else:
                r["t"] = monotonic
                monotonic += 1.0

    return norm_rows


def _only_agent_rows(decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to rows that carry an agent identity."""
    return [
        e for e in decisions
        if isinstance(e, dict)
        and (e.get("agent") is not None or "actor_type" in e)
    ]


def _total_time(
    decisions: List[Dict[str, Any]],
    explicit_t: Optional[float],
) -> float:
    """
    Prefer explicit_t; else use t-range; else fallback to timestamp span.
    """
    if explicit_t is not None:
        return float(explicit_t)
    if not decisions:
        return 0.0
    # t-range (always present after normalization)
    try:
        t_vals = [float(e.get("t") or 0.0) for e in decisions]
        span = max(0.0, max(t_vals) - min(t_vals))
        if span > 0:
            return span
    except (TypeError, ValueError):
        pass
    # Fallback: timestamp span
    ts_vals = [
        e["timestamp"] for e in decisions
        if isinstance(e.get("timestamp"), dt.datetime)
    ]
    if ts_vals:
        return max(0.0, _sec(min(ts_vals), max(ts_vals)))
    return 0.0


def _durations(decisions: List[Dict[str, Any]]) -> List[float]:
    """Prefer duration_s; fallback to latency_ms converted to seconds."""
    durs: List[float] = []
    for e in decisions:
        if e.get("duration_s") is not None:
            try:
                durs.append(max(0.0, float(e["duration_s"])))
            except (TypeError, ValueError):
                durs.append(0.0)
        elif e.get("latency_ms") is not None:
            try:
                durs.append(max(0.0, float(e["latency_ms"]) / 1000.0))
            except (TypeError, ValueError):
                durs.append(0.0)
    return durs


def _mean(xs: List[float]) -> float:
    """Arithmetic mean; returns 0.0 for empty input."""
    return sum(xs) / len(xs) if xs else 0.0


def _clip01(x: float) -> float:
    """Clamp to [0, 1]."""
    return max(0.0, min(1.0, x))


def _safe_prob_dist(p: Dict[str, float]) -> Dict[str, float]:
    """Clamp negatives and re-normalise a probability dict."""
    total = sum(max(0.0, float(v)) for v in p.values())
    if total <= 0:
        return {k: 0.0 for k in p}
    return {k: max(0.0, float(v)) / total for k, v in p.items()}


def _aggregate_probs(
    decisions: List[Dict[str, Any]],
    key: str,
) -> Dict[str, float]:
    """
    Average probability vectors over all decisions that have `key`
    (e.g., 'probs' or 'surrogate_probs'), then re-normalise.
    """
    accum: Dict[str, float] = {}
    count = 0
    for e in decisions:
        val = e.get(key)
        if isinstance(val, dict) and val:
            dist = _safe_prob_dist(val)
            for a, p in dist.items():
                accum[a] = accum.get(a, 0.0) + p
            count += 1
    if count == 0 or not accum:
        return {}
    avg = {k: v / count for k, v in accum.items()}
    return _safe_prob_dist(avg)


def _kl_divergence(
    p: Dict[str, float],
    q: Dict[str, float],
    eps: float = 1e-12,
) -> float:
    """KL(P ‖ Q) over the union of keys."""
    kl = 0.0
    for k in set(p) | set(q):
        pk = max(eps, p.get(k, 0.0))
        qk = max(eps, q.get(k, 0.0))
        kl += pk * math.log(pk / qk)
    return kl


def _count(
    decisions: List[Dict[str, Any]],
    pred: Callable[[Dict[str, Any]], bool],
) -> int:
    """Count decisions matching predicate."""
    return sum(1 for e in decisions if pred(e))


def _safe_rt_s(e: Dict[str, Any]) -> Optional[float]:
    """
    Extract a non-negative response time in seconds from a decision dict.

    Tries duration_s first, then latency_ms/1000.
    Returns None when neither field is present or convertible.
    """
    d = _safe_float(e.get("duration_s"))
    if d is not None:
        return max(0.0, d)
    ms = _safe_float(e.get("latency_ms"))
    if ms is not None:
        return max(0.0, ms / 1000.0)
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_metrics(
    *,
    decisions: List[_DecisionInput],
    T: Optional[float] = None,
    baseline_s: Optional[float] = DEFAULT_BASELINE_S,
    rt_max: float = DEFAULT_RT_MAX,
) -> Dict[str, float]:
    """
    Compute collab-session metrics from a list of decision records.

    Returns a dict with keys: F, D, HCL, Tr, A, S, EL, EfficiencyScore.

    Accepts DecisionEvent objects (from an adapter) or plain dicts with
    canonical field names.  Alias resolution must be done upstream.
    """
    decisions = _normalize_decisions(decisions)
    decisions = sorted(decisions, key=lambda e: float(e.get("t") or 0.0))
    agent_rows = _only_agent_rows(decisions)
    n_agents = len(agent_rows)

    total_time = _total_time(agent_rows, T)  # T is the public param name

    # 1) F — interactions per minute (agent-only rows)
    f_score = (n_agents / (total_time / 60.0)) if total_time > 0 else 0.0

    # 2) D — mean atomic action duration (agent-only rows)
    durs = _durations(agent_rows)
    d_score = _mean(durs)

    # 3) HCL — human cognitive load proxy
    #    Use human-labelled rows; fall back through durs → latencies → rt_max.
    human_rt_vals: List[float] = [
        rt
        for e in agent_rows
        if (
            str(e.get("actor_type", "")).lower() == "human"
            or str(e.get("agent", "")).upper().startswith("H")
        )
        for rt in [_safe_rt_s(e)]
        if rt is not None
    ]
    latencies_s: List[float] = [
        v / 1000.0
        for e in agent_rows
        for v in [_safe_float(e.get("latency_ms"))]
        if v is not None
    ]
    if human_rt_vals:
        mean_rt = _mean(human_rt_vals)
    elif durs:
        mean_rt = _mean(durs)
    elif latencies_s:
        mean_rt = _mean(latencies_s)
    else:
        mean_rt = rt_max if rt_max > 0 else 1.0
    hcl = _clip01(1.0 - (mean_rt / rt_max if rt_max > 0 else 1.0))

    # 4) Tr — trust / reliability
    #    Score only rows that are explicitly labelled OR error events.
    labeled = 0
    errors = 0
    for e in agent_rows:
        if e.get("correct") is not None:
            labeled += 1
            if e.get("correct") is False:
                errors += 1
    for e in decisions:
        if str(e.get("event_type", "")).lower() == "error":
            labeled += 1
            errors += 1
    tr_score = _clip01(1.0 - (errors / labeled if labeled > 0 else 0.0))

    # 5) A — adaptability; bounded [-1, 1] via tanh
    if n_agents > 0:
        k = max(1, int(0.2 * n_agents))
        early = agent_rows[:k]
        late = agent_rows[-k:]

        def _acc(arr: List[Dict[str, Any]]) -> float:
            have = [e for e in arr if e.get("correct") is not None]
            if not have:
                return 1.0  # neutral when unlabelled
            return sum(1 for e in have if e.get("correct") is True) / len(have)

        acc_early = _acc(early)
        acc_late = _acc(late)
        raw_a = (acc_late - acc_early) / max(1e-9, acc_early)
        a_score: float = math.tanh(raw_a)
    else:
        a_score = 0.0

    # 6) S — surrogate similarity (agent rows only)
    p_h = _aggregate_probs(agent_rows, "probs")
    p_s = _aggregate_probs(agent_rows, "surrogate_probs")
    if p_h and p_s:
        s_score: float = math.exp(-_kl_divergence(p_h, p_s))
    else:
        matches = compared = 0
        for e in agent_rows:
            sa = e.get("surrogate_action")
            if sa is not None:
                compared += 1
                if e.get("action") == sa:
                    matches += 1
        s_score = (matches / compared) if compared > 0 else 0.0
    s_score = _clip01(s_score)

    # 7) EL — effort loss vs baseline
    if baseline_s is not None and baseline_s > 0 and total_time > 0:
        el_score = max(0.0, (total_time - baseline_s) / baseline_s)
    else:
        el_score = 0.0

    efficiency = 1.0 / (1.0 + el_score)  # el_score >= 0 always

    # ---- Gentle shaping: off-role penalty + progress bonus ----
    offrole_count = sum(1 for e in agent_rows if bool(e.get("off_role_action")))
    offrole_rate = (offrole_count / n_agents) if n_agents > 0 else 0.0

    progress_count = _count(
        decisions,
        lambda e: str(e.get("event_type", "")).lower()
        in {"checklist_progress", "progress"},
    )
    progress_rate = (progress_count / max(1.0, total_time)) if total_time > 0 else 0.0

    efficiency *= 1.0 - _OFFROLE_PENALTY_WEIGHT * _clip01(offrole_rate)
    efficiency *= 1.0 + _PROGRESS_BONUS_WEIGHT * _clip01(progress_rate)
    efficiency = _clip01(efficiency)

    return {
        "F":               float(f_score),
        "D":               float(d_score),
        "HCL":             float(hcl),
        "Tr":              float(tr_score),
        "A":               float(a_score),
        "S":               float(s_score),
        "EL":              float(el_score),
        "EfficiencyScore": float(efficiency),
    }


def compute_metrics_by_agent(
    decisions: List[_DecisionInput],
    **kw: Any,
) -> Dict[str, Dict[str, float]]:
    """
    Run compute_metrics() separately for each agent found in decisions.

    Returns {agent_id: metrics_dict}.  Rows with no agent identity are
    grouped under the key "unknown" rather than silently dropped.
    """
    out: Dict[str, Dict[str, float]] = {}
    decs = _normalize_decisions(decisions)
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for d in decs:
        agent_key = str(d.get("agent") or "unknown")
        by_agent.setdefault(agent_key, []).append(d)
    for agent, arr in by_agent.items():
        out[agent] = compute_metrics(decisions=arr, **kw)
    return out
