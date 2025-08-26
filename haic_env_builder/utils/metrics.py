from __future__ import annotations
from typing import List, Dict, Any
import math

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def _safe_mean(xs: List[float], default: float = 0.0) -> float:
    return sum(xs) / len(xs) if xs else default

def _normalize_latency(ms: float, max_ms: int = 3000) -> float:
    """Return 0..1 where 1 is fast (low ms) and 0 is slow (high ms)."""
    return _clamp(1.0 - (ms / max_ms), 0.0, 1.0)

def _cv(xs: List[float]) -> float:
    """Coefficient of variation (std/mean); 0 if undefined."""
    if len(xs) < 2:
        return 0.0
    m = _safe_mean(xs)
    if m <= 0:
        return 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return (var ** 0.5) / m

def compute_metrics(decisions: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute human-centric metrics from a generic 'decisions' log.

    Each decision dict may contain (all optional, robust if missing):
      - step: int
      - agent: str
      - source: 'human' | 'ai'        # who initiated the action
      - action: str                   # action label
      - latency_ms: int/float         # time until this action completed
      - accepted: bool                # if human accepted AI suggestion
      - override: bool                # if human overrode AI
      - error: bool                   # if action led to error/violation
      - correction: bool              # if action corrected a previous error
      - risk: float (0..1)            # risk score of action

    Returns scores in [0,1] for:
      F (Fluency), D (Delay), HCL (Human Cognitive Load proxy),
      Tr (Trust), A (Adaptability), S (Safety), EL (Effort/Load).
    """

    # --- Extract signals with graceful fallbacks ----------------------------
    latencies = [float(d.get("latency_ms", 1000.0)) for d in decisions]
    sources   = [d.get("source", "ai") for d in decisions]
    actions   = [d.get("action", "") for d in decisions]

    accepted_flags = [bool(d["accepted"]) for d in decisions if "accepted" in d]
    ai_acceptables = [bool(d.get("accepted", False)) for d in decisions if d.get("source") == "ai"]

    override_flags = [bool(d["override"]) for d in decisions if "override" in d]
    error_flags    = [bool(d["error"])    for d in decisions if "error"    in d]
    corrections    = [bool(d["correction"]) for d in decisions if "correction" in d]
    risks          = [float(d["risk"]) for d in decisions if "risk" in d]

    # Alternation of sources (turn-taking fluency)
    alternations = 0
    for i in range(1, len(sources)):
        if sources[i] != sources[i-1]:
            alternations += 1
    alternation_rate = alternations / max(1, len(sources) - 1)

    # Latency stats
    mean_latency = _safe_mean(latencies, default=1000.0)
    cv_latency   = _cv(latencies)
    fast_score   = _normalize_latency(mean_latency)      # 1=fast, 0=slow
    stability    = 1.0 - _clamp(cv_latency, 0.0, 1.0)    # 1=stable timings

    # Action context switches (how often action label changes)
    switches = 0
    for i in range(1, len(actions)):
        if actions[i] != actions[i-1]:
            switches += 1
    switch_rate = switches / max(1, len(actions) - 1)

    # Long latency rate (proxy for load)
    long_latency_rate = sum(1 for t in latencies if t > 2000) / max(1, len(latencies))

    # Error/risk rates
    error_rate = sum(1 for e in error_flags if e) / max(1, len(error_flags)) if error_flags else 0.0
    high_risk_rate = sum(1 for r in risks if r > 0.7) / max(1, len(risks)) if risks else 0.0

    # Corrections (rework)
    rework_rate = sum(1 for c in corrections if c) / max(1, len(corrections)) if corrections else 0.0

    # --- Metrics -------------------------------------------------------------
    # F: Fluency – smooth turn-taking and stable, fast pace
    F = _clamp(0.5 * alternation_rate + 0.3 * fast_score + 0.2 * stability)

    # D: Delay – the inverse of mean latency (fast is good)
    D = fast_score

    # HCL: Human Cognitive Load – higher with more switches, long delays, rework
    raw_hcl = (switch_rate + long_latency_rate + rework_rate) / 3.0
    HCL = _clamp(raw_hcl)

    # Tr: Trust – preference for accepting AI suggestions, or few overrides
    if ai_acceptables:
        Tr = _safe_mean([1.0 if a else 0.0 for a in ai_acceptables], default=0.5)
    elif override_flags:
        Tr = 1.0 - _safe_mean([1.0 if o else 0.0 for o in override_flags], default=0.5)
    else:
        Tr = 0.5  # unknown → neutral

    # A: Adaptability – improvement of speed over time (2nd half faster than 1st)
    if len(latencies) >= 4:
        mid = len(latencies) // 2
        first = _safe_mean(latencies[:mid], 1000.0)
        second = _safe_mean(latencies[mid:], 1000.0)
        delta_ms = first - second  # positive means improved (faster)
        # squash to 0..1 via sigmoid centered at 0 with scale 1000ms
        A = 1.0 / (1.0 + math.exp(-delta_ms / 1000.0))
    else:
        A = 0.5

    # S: Safety – fewer errors and risky actions
    S = _clamp(1.0 - (0.7 * error_rate + 0.3 * high_risk_rate))

    # EL: Effort/Load – human contribution cost (count * latency)
    human_lat = [latencies[i] for i, s in enumerate(sources) if s == "human"]
    if human_lat:
        human_load = _safe_mean(human_lat)  # ms
        EL = 1.0 - _normalize_latency(human_load, max_ms=4000)  # higher = more effort
    else:
        EL = 0.3  # assume some low effort when no explicit human steps logged

    return {
        "F": round(F, 3),
        "D": round(D, 3),
        "HCL": round(HCL, 3),
        "Tr": round(Tr, 3),
        "A": round(A, 3),
        "S": round(S, 3),
        "EL": round(EL, 3),
    }
