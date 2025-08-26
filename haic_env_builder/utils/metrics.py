# haic_env_builder/utils/metrics.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import math

DEFAULT_RT_MAX = 5.0  # seconds
DEFAULT_BASELINE_S = None

def _total_time(decisions: List[Dict[str, Any]], explicit_T: Optional[float]) -> float:
    if explicit_T is not None:
        return float(explicit_T)
    if not decisions:
        return 0.0
    t0 = float(decisions[0]["t"])
    tN = float(decisions[-1]["t"])
    return max(0.0, tN - t0)

def _durations(decisions: List[Dict[str, Any]]) -> List[float]:
    # Prefer explicit duration_s, fallback to latency_ms (sec)
    durs = []
    for e in decisions:
        if e.get("duration_s") is not None:
            durs.append(max(0.0, float(e["duration_s"])))
        elif e.get("latency_ms") is not None:
            durs.append(max(0.0, float(e["latency_ms"]) / 1000.0))
    return durs

def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0

def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _safe_prob_dist(p: Dict[str, float]) -> Dict[str, float]:
    # normalize to sum=1; ignore negative, treat missing as 0
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

def compute_metrics(
    *,
    decisions: List[Dict[str, Any]],
    T: Optional[float] = None,
    baseline_s: Optional[float] = DEFAULT_BASELINE_S,
    rt_max: float = DEFAULT_RT_MAX,
) -> Dict[str, float]:
    """
    Returns dict with keys: F, D, HCL, Tr, A, S, EL
    Assumes decisions are sorted by 't' ascending.
    """
    N = len(decisions)
    total_time = _total_time(decisions, T)

    # 1) F: interactions per minute (can be > 1, that's OK)
    F = (N / (total_time / 60.0)) if total_time > 0 else 0.0

    # 2) D: mean atomic action duration (sec)
    durs = _durations(decisions)
    D = _mean(durs)

    # 3) HCL: 1 - meanRT/RTmax (human events preferred; else overall)
    human_rts = [
        (float(e["duration_s"]) if e.get("duration_s") is not None
         else float(e.get("latency_ms", 0.0)) / 1000.0)
        for e in decisions
        if e.get("actor_type") == "human"
    ]
    mean_rt = _mean(human_rts) if human_rts else _mean(durs)
    HCL = _clip01(1.0 - (mean_rt / rt_max if rt_max > 0 else 1.0))

    # 4) Tr: 1 - errors/N (error if correct==False or event_type=='error')
    errors = 0
    for e in decisions:
        if e.get("correct") is False:
            errors += 1
        elif e.get("event_type") == "error":
            errors += 1
    Tr = _clip01(1.0 - (errors / N if N > 0 else 0.0))

    # 5) A: adaptability = (acc_late - acc_early) / max(1e-9, acc_early)
    if N > 0:
        k = max(1, int(0.2 * N))
        early = decisions[:k]
        late = decisions[-k:]

        def acc(arr):
            have = [e for e in arr if e.get("correct") is not None]
            if not have:
                return 1.0  # if nothing is labeled, assume correct to avoid NaN
            return sum(1 for e in have if e.get("correct") is True) / len(have)

        acc_early = acc(early)
        acc_late = acc(late)
        denom = max(1e-9, acc_early)
        A = (acc_late - acc_early) / denom
    else:
        A = 0.0

    # 6) S: surrogate similarity
    # Prefer probability-based KL similarity if both P_human and P_surrogate exist.
    P_h = _aggregate_probs(decisions, "probs")
    P_s = _aggregate_probs(decisions, "surrogate_probs")
    if P_h and P_s:
        D_kl = _kl_divergence(P_h, P_s)   # >= 0
        S = math.exp(-D_kl)               # in (0,1], 1 when identical
    else:
        # Fallback: simple action agreement rate if surrogate_action is present
        matches, compared = 0, 0
        for e in decisions:
            if "surrogate_action" in e:
                compared += 1
                if e.get("action") == e.get("surrogate_action"):
                    matches += 1
        S = (matches / compared) if compared > 0 else 0.0
    S = _clip01(S)

    # 7) EL: effort/efficiency loss vs baseline
    if baseline_s is not None and baseline_s > 0 and total_time > 0:
        EL = max(0.0, (total_time - baseline_s) / baseline_s)
    else:
        EL = 0.0

    return {
        "F": float(F),
        "D": float(D),
        "HCL": float(HCL),
        "Tr": float(Tr),
        "A": float(A),
        "S": float(S),
        "EL": float(EL),
    }
