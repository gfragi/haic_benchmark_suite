# haic_env_builder/utils/metrics.py

from __future__ import annotations
from typing import List, Dict, Any, Optional
import math

def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b not in (0, None) else default

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def compute_metrics(
    decisions: List[Dict[str, Any]],
    total_time: float,
    *,
    steps: Optional[int] = None,
    num_agents: Optional[int] = None,
    dt: Optional[float] = None,
    latency_ref: float = 1.0,
) -> Dict[str, float]:
    """
    Compute F, D, HCL, Tr, A, S, EL with proper normalization.
    Assumes decisions entries may contain: t, actor, action, latency, accepted, reward.
    """

    # ---- Derive fallbacks if not provided ----
    # Unique time stamps -> infer steps when not provided
    unique_ts = sorted(set(d.get("t") for d in decisions if "t" in d))
    if steps is None:
        steps = len(unique_ts)

    if num_agents is None:
        # Prefer explicit num_agents; if not provided, try to infer unique 'agent_name' (if you log it)
        # fallback to count actors per timestamp average (can be off if variable participation)
        # Simple safe fallback:
        # estimate by rounding observed_interactions / steps
        obs = len(decisions)
        num_agents = max(1, round(obs / steps)) if steps else 1

    # ---- F: Interaction Frequency (utilization) ----
    # Option A: utilization per step (recommended)
    max_possible = steps * num_agents
    F = clamp01(safe_div(len(decisions), max_possible, default=0.0))

    # ---- D: Interaction Duration (normalized average latency) ----
    latencies = [d.get("latency") for d in decisions if isinstance(d.get("latency"), (int, float))]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    # normalize by reference (e.g., 1s). You can invert if you want "shorter is better".
    # Here we map lower latency to higher score: D = 1 - (avg_latency / latency_ref), clipped.
    D = clamp01(1.0 - safe_div(avg_latency, latency_ref, default=0.0))

    # ---- HCL: Human Cognitive Load proxy (normalized by max latency) ----
    # If you prefer the paper’s version: HCL = 1 - RT_avg / RT_max
    if latencies:
        rt_max = max(latencies)
        HCL = clamp01(1.0 - safe_div(avg_latency, rt_max, default=0.0))
    else:
        HCL = 0.0

    # ---- Tr: Trust proxy (acceptance rate) ----
    accepts = [d.get("accepted") for d in decisions if d.get("accepted") is not None]
    if accepts:
        Tr = clamp01(sum(1 for a in accepts if a) / len(accepts))
    else:
        Tr = 0.0

    # ---- A: Adaptability (delta reward normalized) ----
    rewards = [d.get("reward") for d in decisions if isinstance(d.get("reward"), (int, float))]
    if rewards:
        r0, rN = rewards[0], rewards[-1]
        # normalize by number of steps (so longer runs don’t automatically inflate A)
        A = clamp01(safe_div((rN - r0), max(1, steps)))
    else:
        A = 0.0

    # ---- S: Surrogate Similarity (placeholder: 0 unless you compute behavior similarity) ----
    # Keep as-is until you plug in your BC/surrogate distributional comparison.
    S = 0.0

    # ---- EL: Error Load (time-weighted error rate; here we use 1 - acceptance if available) ----
    # If no 'accepted', fall back to latency-based penalty
    if accepts:
        err_rate = sum(1 for a in accepts if not a) / len(accepts)
        EL = clamp01(err_rate)
    else:
        # simple fallback: penalize long latencies
        EL = clamp01(safe_div(avg_latency, latency_ref, default=0.0))

    return {
        "F": F,
        "D": D,
        "HCL": HCL,
        "Tr": Tr,
        "A": A,
        "S": S,
        "EL": EL,
    }
