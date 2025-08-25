from typing import List, Dict, Any
from itertools import combinations
from collections import Counter
import math


def _avg(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _avg(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 1.0


def compute_metrics_from_log(
    task_name: str,
    agents: List[str],
    decisions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Deterministic, explainable metrics over raw decisions.
    Produces: F, D, HCL, Tr, A, S, EL (+ basic counts).
    """

    # basic aggregates
    total_actions = len(decisions)
    per_agent = {a: [] for a in agents}
    for d in decisions:
        per_agent[d["agent"]].append(d)

    # --- EL (Efficiency / Latency)
    avg_latency = _avg([d["latency_ms"] for d in decisions])
    EL = max(0.0, 1.0 - (avg_latency / 1000.0))  # 0..1 where lower latency -> higher score

    # --- D (Diversity of actions)
    all_actions = [d["action"] for d in decisions]
    unique_actions = len(set(all_actions))
    # normalize by a small fixed universe to keep 0..1 (you can swap for domain-specific)
    action_universe = 8
    D = min(1.0, unique_actions / action_universe)

    # --- Tr (Trust) = accepted / suggested
    suggested = sum(1 for d in decisions if d["ai_suggested"])
    accepted = sum(1 for d in decisions if d["human_accepted"])
    Tr = (accepted / suggested) if suggested else 0.0

    # --- HCL (Human-Centeredness)
    # for now, treat as acceptance rate weighted by success
    successes = sum(1 for d in decisions if d["success"])
    HCL = 0.5 * (accepted / total_actions if total_actions else 0.0) + \
          0.5 * (successes / total_actions if total_actions else 0.0)

    # --- A (Adaptability)
    # compare success rate first half vs second half
    mid = total_actions // 2
    succ_first = sum(1 for d in decisions[:mid] if d["success"])
    succ_second = sum(1 for d in decisions[mid:] if d["success"])
    rate_first = succ_first / max(1, mid)
    rate_second = succ_second / max(1, total_actions - mid)
    A = max(0.0, rate_second - rate_first)  # improvement

    # --- S (Similarity) average pairwise Jaccard of action sets between agents
    action_sets = {a: set(d["action"] for d in per_agent[a]) for a in agents}
    if len(agents) < 2:
        S = 1.0
    else:
        sims = [_jaccard(action_sets[a], action_sets[b]) for a, b in combinations(agents, 2)]
        S = _avg(sims)

    # --- F (Fairness): balance of successes by agent (lower std -> higher fairness)
    succ_counts = [sum(1 for d in per_agent[a] if d["success"]) for a in agents]
    mean_succ = _avg(succ_counts)
    if mean_succ == 0:
        F = 0.0
    else:
        # normalized fairness = 1 - (std / mean), clipped to [0,1]
        F = max(0.0, min(1.0, 1.0 - (_std(succ_counts) / mean_succ)))

    # Optional: interpretable buckets
    per_action_counts = dict(Counter(all_actions))
    per_agent_success = {a: sum(1 for d in per_agent[a] if d["success"]) for a in agents}
    per_agent_accepted = {a: sum(1 for d in per_agent[a] if d["human_accepted"]) for a in agents}

    return {
        "summary": {
            "task": task_name,
            "total_actions": total_actions,
            "avg_latency_ms": avg_latency,
        },
        "metrics": {
            "F": round(F, 3),
            "D": round(D, 3),
            "HCL": round(HCL, 3),
            "Tr": round(Tr, 3),
            "A": round(A, 3),
            "S": round(S, 3),
            "EL": round(EL, 3),
        },
        "by_agent": {
            "successes": per_agent_success,
            "accepted": per_agent_accepted,
        },
        "by_action": per_action_counts,
    }
