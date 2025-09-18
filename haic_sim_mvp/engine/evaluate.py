
from typing import Dict, Any

def compute_metrics(log: Dict[str, Any]) -> Dict[str, Any]:
    decisions = log.get("decisions", [])
    n = len(decisions)
    if n == 0: return {"n": 0}
    correct_total = ai_c = h_c = ai_n = h_n = defer = latency = 0
    for d in decisions:
        eff = d.get("effect", {})
        is_ai, is_h = "ai_label" in eff, "human_label" in eff
        if d.get("correct"): correct_total += 1; ai_c += is_ai; h_c += is_h and 1 or 0 if d.get("correct") else 0
        ai_n += is_ai; h_n += is_h; defer += 1 if eff.get("deferred") else 0
        latency += d.get("latency_ms") or 0
    return {
        "n": n,
        "accuracy": correct_total / n,
        "ai_accuracy": (ai_c / ai_n) if ai_n else None,
        "human_accuracy": (h_c / h_n) if h_n else None,
        "defer_rate": defer / n,
        "avg_latency_ms": latency / n,
    }
