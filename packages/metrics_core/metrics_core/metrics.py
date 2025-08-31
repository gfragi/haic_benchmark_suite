# haic_env_builder/utils/metrics.py
from __future__ import annotations
from typing import List, Dict, Any, Optional, Callable
import math

DEFAULT_RT_MAX = 5.0   # seconds
DEFAULT_BASELINE_S = None

# Soft weights for composite EfficiencyScore shaping
_OFFROLE_PENALTY_WEIGHT = 0.35   # 0..1 penalty multiplier
_PROGRESS_BONUS_WEIGHT = 0.10    # 0..1 bonus multiplier


def _only_agent_rows(decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to rows that represent agent actions (i.e., have an 'agent' field)."""
    return [e for e in decisions if isinstance(e, dict) and ("agent" in e)]


def _total_time(decisions: List[Dict[str, Any]], explicit_T: Optional[float]) -> float:
    if explicit_T is not None:
        return float(explicit_T)
    if not decisions:
        return 0.0
    t0 = float(decisions[0].get("t", 0.0))
    tN = float(decisions[-1].get("t", t0))
    return max(0.0, tN - t0)


def _durations(decisions: List[Dict[str, Any]]) -> List[float]:
    # Prefer explicit duration_s, fallback to latency_ms (sec)
    durs: List[float] = []
    for e in decisions:
        if e.get("duration_s") is not None:
            try:
                durs.append(max(0.0, float(e["duration_s"])))
            except Exception:
                durs.append(0.0)
        elif e.get("latency_ms") is not None:
            try:
                durs.append(max(0.0, float(e["latency_ms"]) / 1000.0))
            except Exception:
                durs.append(0.0)
    return durs


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe_prob_dist(p: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(0.0, float(v)) for v in p.values())
    if total <= 0:
        return {k: 0.0 for k in p.keys()}
    return {k: max(0.0, float(v)) / total for k, v in p.items()}


def _aggregate_probs(decisions: List[Dict[str, Any]], key: str) -> Dict[str, float]:
    """
    Average probability vectors over all decisions that have `key` (e.g., 'probs' or 'surrogate_probs'),
    then re-normalize. This yields P_human or P_surrogate for S.
    """
    accum: Dict[str, float] = {}
    count = 0
    for e in decisions:
        if key in e and isinstance(e[key], dict) and e[key]:
            dist = _safe_prob_dist(e[key])
            for a, p in dist.items():
                accum[a] = accum.get(a, 0.0) + p
            count += 1
    if count == 0 or not accum:
        return {}
    # average and renormalize
    avg = {k: v / count for k, v in accum.items()}
    return _safe_prob_dist(avg)


def _kl_divergence(p: Dict[str, float], q: Dict[str, float], eps: float = 1e-12) -> float:
    """
    KL(P||Q) over the union of keys. Both are probabilities over actions.
    """
    keys = set(p.keys()) | set(q.keys())
    kl = 0.0
    for k in keys:
        pk = max(eps, p.get(k, 0.0))
        qk = max(eps, q.get(k, 0.0))
        kl += pk * math.log(pk / qk)
    return kl


def _count(decisions: List[Dict[str, Any]], pred: Callable[[Dict[str, Any]], bool]) -> int:
    return sum(1 for e in decisions if pred(e))


def compute_metrics(
    *,
    decisions: List[Dict[str, Any]],
    T: Optional[float] = None,
    baseline_s: Optional[float] = DEFAULT_BASELINE_S,
    rt_max: float = DEFAULT_RT_MAX,
) -> Dict[str, float]:
    """
    Returns dict with keys: F, D, HCL, Tr, A, S, EL, EfficiencyScore
    Assumes decisions are sorted by 't' ascending.
    """
    decisions = sorted(decisions, key=lambda e: float(e.get("t", float("inf"))))
    agent_rows = _only_agent_rows(decisions)
    N_agents = len(agent_rows)

    # --- Time window over agent rows only ---
    total_time = _total_time(agent_rows, T)

    # 1) F: interactions per minute (agent-only)
    F = (N_agents / (total_time / 60.0)) if total_time > 0 else 0.0

    # 2) D: mean atomic action duration (agent-only)
    durs = _durations(agent_rows)
    D = _mean(durs)

    # 3) HCL: prefer human agent rows; fallback to agent rows
    human_rts = [
        (float(e["duration_s"]) if e.get("duration_s") is not None
         else float(e.get("latency_ms", 0.0)) / 1000.0)
        for e in agent_rows
        if e.get("actor_type") == "human"
    ]
    latencies_s = [
        float(e.get("latency_ms", 0.0)) / 1000.0
        for e in agent_rows
        if e.get("latency_ms") is not None
    ]
    if human_rts:
        mean_rt = _mean(human_rts)
    elif durs:
        mean_rt = _mean(durs)
    elif latencies_s:
        mean_rt = _mean(latencies_s)
    else:
        mean_rt = rt_max if rt_max > 0 else 1.0
    HCL = _clip01(1.0 - (mean_rt / rt_max if rt_max > 0 else 1.0))

    # 4) Tr: only score rows that are explicitly labeled OR explicit error events
    labeled = 0
    errors = 0
    # labeled agent actions (carry 'correct')
    for e in agent_rows:
        if e.get("correct") is not None:
            labeled += 1
            if e.get("correct") is False:
                errors += 1
    # explicit error events (env or agent), count as labeled too
    for e in decisions:
        if str(e.get("event_type", "")).lower() == "error":
            labeled += 1
            errors += 1
    Tr = _clip01(1.0 - (errors / labeled if labeled > 0 else 0.0))

    # 5) A: adaptability on agent rows; clamp to [-1, 1] via tanh
    if N_agents > 0:
        k = max(1, int(0.2 * N_agents))
        early = agent_rows[:k]
        late = agent_rows[-k:]

        def acc(arr):
            have = [e for e in arr if e.get("correct") is not None]
            if not have:
                return 1.0  # neutral if unlabeled
            return sum(1 for e in have if e.get("correct") is True) / len(have)

        acc_early = acc(early)
        acc_late = acc(late)
        denom = max(1e-9, acc_early)
        raw_A = (acc_late - acc_early) / denom
        A = math.tanh(raw_A)  # bounded [-1, 1]
    else:
        A = 0.0

    # 6) S: surrogate similarity (use agent rows)
    P_h = _aggregate_probs(agent_rows, "probs")
    P_s = _aggregate_probs(agent_rows, "surrogate_probs")
    if P_h and P_s:
        D_kl = _kl_divergence(P_h, P_s)
        S = math.exp(-D_kl)
    else:
        matches, compared = 0, 0
        for e in agent_rows:
            if "surrogate_action" in e:
                compared += 1
                if e.get("action") == e.get("surrogate_action"):
                    matches += 1
        S = (matches / compared) if compared > 0 else 0.0
    S = _clip01(S)

    # 7) EL: effort/efficiency loss vs baseline (use agent-window time)
    if baseline_s is not None and baseline_s > 0 and total_time > 0:
        EL = max(0.0, (total_time - baseline_s) / baseline_s)
    else:
        EL = 0.0

    # Base efficiency from EL only
    EfficiencyScore = 1.0 / (1.0 + float(EL)) if EL >= 0 else 1.0

    # ---- Gentle shaping with off-role and progress signals (if present) ----
    def _count_pred(rows: List[Dict[str, Any]], pred: Callable[[Dict[str, Any]], bool]) -> int:
        return sum(1 for e in rows if pred(e))

    # Off-role: consider agent rows only
    offrole_count = _count_pred(agent_rows, lambda e: bool(e.get("off_role_action")))
    offrole_rate = (offrole_count / N_agents) if N_agents > 0 else 0.0

    # Progress: allow env events to contribute
    progress_count = _count(decisions, lambda e: str(e.get("event_type", "")).lower() in {"checklist_progress", "progress"})
    progress_rate = (progress_count / max(1.0, total_time)) if total_time > 0 else 0.0  # events/sec

    EfficiencyScore *= (1.0 - _OFFROLE_PENALTY_WEIGHT * _clip01(offrole_rate))
    EfficiencyScore *= (1.0 + _PROGRESS_BONUS_WEIGHT * _clip01(progress_rate))
    EfficiencyScore = _clip01(EfficiencyScore)

    return {
        "F": float(F),
        "D": float(D),
        "HCL": float(HCL),
        "Tr": float(Tr),
        "A": float(A),
        "S": float(S),
        "EL": float(EL),
        "EfficiencyScore": float(EfficiencyScore),
    }


def compute_metrics_by_agent(decisions: List[Dict[str, Any]], **kw) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for d in _only_agent_rows(decisions):
        by_agent.setdefault(str(d.get("agent")), []).append(d)
    for agent, decs in by_agent.items():
        out[agent] = compute_metrics(decisions=decs, **kw)
    return out
