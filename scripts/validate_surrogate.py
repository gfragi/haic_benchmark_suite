"""
validate_surrogate.py

Compares MarkovSurrogateSC-generated sessions against the real Smart City
pilot data it was fitted from, using the platform's own
metrics_core.interaction_metrics.compute_metrics() wherever possible, plus
an explicit Jensen-Shannon-based Surrogate Similarity (S) computation.

Run: python scripts/validate_surrogate.py

--- Last run output ---

=== PART A: Real pilot baseline (n=164) ===
  Metric  | Value
  Tr      |  0.701
  HCL     |  0.648
  EL      |  0.131  (manual per-item calc using ai_reject=77.5s/ai_flag=222.2s as baseline (see module docstring))
  A       |    N/A  (insufficient labeled events in an early/late split)
  F       |  0.797
  S       | N/A  (real events carry no surrogate_probs - not applicable)

=== PART B: Surrogate sessions (n=20 x 164 items, aggregate persona) ===
  Metric  |     Mean |      Std |      Min |      Max
  Tr      |    0.616 |    0.056 |    0.488 |    0.707
  HCL     |    0.650 |    0.020 |    0.615 |    0.694
  EL      |      N/A |      N/A |      N/A |      N/A
  A       |    0.005 |    0.173 |   -0.291 |    0.343
  F       |    0.801 |    0.033 |    0.747 |    0.877

=== PART C: Surrogate Similarity S ===
  Mean S across 20 sessions: 1.000 ± 0.000
  Expected range: 0.85-1.0 for aggregate persona (by construction - see module docstring)

=== PART D: Per-operator Tr comparison ===
  Op   |  Real Tr |    Surrogate Tr (mean±std) | n_real |    Delta
  1    |  0.606 |                0.731±0.118 |     33 |  0.125
  2    |  0.606 |                0.400±0.082 |     33 | -0.206
  3    |  0.667 |                0.506±0.107 |     33 | -0.160
  4    |  0.636 |                0.625±0.099 |     33 | -0.011
  5    |  1.000 |                0.912±0.046 |     32 | -0.088

--- Delta summary (B vs A) ---
  Metric  |     Real |  Surrogate mean |  Delta abs |  Delta %
  Tr      |    0.701 |           0.616 |     -0.085 |   -12.1%
  HCL     |    0.648 |           0.650 |     +0.002 |    +0.4%
  F       |    0.797 |           0.801 |     +0.004 |    +0.5%
  (EL/A/S omitted - not available on both sides, see notes above)
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "surrogate"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "metrics_core"))
from surrogate.markov_sc import MarkovSurrogateSC  # noqa: E402
from metrics_core.interaction_metrics import compute_metrics  # noqa: E402

REAL_DATA_PATH = "haic_sim_mvp/examples/events_all_v0_patched.json"
MODEL_PATH = "data/sc_markov_model.json"
RT_MAX_S = 300.0

# Empirical mean operator durations from Step 1 - used as a rough
# "no-AI baseline" approximation for EL on the real data (per the task
# spec; note this is an approximation, not a true without-AI baseline,
# since it's actually the WITH-AI operator duration itself).
BASELINE_BY_AI_ACTION = {"ai_reject": 77.5, "ai_flag": 222.2}

METRICS = ["Tr", "HCL", "EL", "A", "F", "S"]


def load_real_records() -> list[dict[str, Any]]:
    """Extract the 164 real applications that reached operator review
    (ai_evaluated + operator_verified pairs) - the population the Markov
    model was fitted from. The 402 auto-accepted sessions are excluded:
    the surrogate never generates those either (ai_accept has zero
    sampling weight), so including them would compare different
    populations."""
    data = json.loads(Path(REAL_DATA_PATH).read_text(encoding="utf-8"))
    records = []
    for session in data["logs"]:
        decisions = session.get("decisions") or []
        ai_ev = next((d for d in decisions if d.get("action") == "ai_evaluated"), None)
        op_ev = next((d for d in decisions if d.get("action") == "operator_verified"), None)
        if ai_ev is None or op_ev is None:
            continue
        records.append({"ai_event": ai_ev, "op_event": op_ev})
    return records


def _ai_action_of(ai_event: dict) -> str:
    """Canonical ai_action for one real ai_evaluated event."""
    raw = (ai_event.get("payload") or {}).get("ai_decision")
    return {"Accepted": "ai_accept", "Rejected": "ai_reject", "Flagged for verification": "ai_flag"}.get(raw)


def compute_metrics_safe(decisions: list[dict], **kwargs) -> dict[str, float | None]:
    """compute_metrics(), but never raises - a per-metric failure becomes
    None rather than aborting the whole comparison."""
    try:
        return compute_metrics(decisions=decisions, **kwargs)
    except Exception as e:
        print(f"  [compute_metrics failed: {e}] - all metrics recorded as None")
        return {m: None for m in METRICS}


def real_baseline() -> dict[str, Any]:
    """Part A: real pilot metrics from the 164 operator-reviewed sessions,
    as one flat decisions list fed to compute_metrics() (uses real
    timestamps, so F/A reflect genuine pilot pacing/trend, not synthetic
    spacing). EL is computed manually per-item since compute_metrics()
    only accepts a single baseline_s per call but the "no-AI baseline"
    differs by ai_action (see BASELINE_BY_AI_ACTION)."""
    records = load_real_records()
    decisions = []
    for r in records:
        decisions.append(r["ai_event"])
        decisions.append(r["op_event"])

    result = compute_metrics_safe(decisions, T=None, baseline_s=None, rt_max=RT_MAX_S)

    el_values = []
    for r in records:
        ai_action = _ai_action_of(r["ai_event"])
        baseline = BASELINE_BY_AI_ACTION.get(ai_action)
        dur = r["op_event"].get("duration_s")
        if baseline and dur is not None:
            el_values.append(max(0.0, (dur - baseline) / baseline))
    el_manual = float(np.mean(el_values)) if el_values else None

    return {
        "n": len(records),
        "Tr": result.get("Tr"),
        "HCL": result.get("HCL"),
        "EL": el_manual,
        "EL_note": "manual per-item calc using ai_reject=77.5s/ai_flag=222.2s as baseline (see module docstring)",
        "A": result.get("A"),
        "A_note": None if result.get("A") is not None else "insufficient labeled events in an early/late split",
        "F": result.get("F"),
        "S": None,
        "S_note": "real events carry no surrogate_probs - not applicable",
    }


def surrogate_batch_metrics(persona: str, seed: int, n_sessions: int, n_items: int) -> tuple[list[dict], MarkovSurrogateSC]:
    """Part B: generate a batch of surrogate sessions and run
    compute_metrics() on each (baseline_s=None, per the task spec -
    EL is expected to come back None)."""
    surrogate = MarkovSurrogateSC(model_path=MODEL_PATH, persona=persona, seed=seed)
    sessions = surrogate.generate_batch(n_sessions=n_sessions, n_items=n_items, rt_max_s=RT_MAX_S, baseline_s=None)

    per_session = []
    for session in sessions:
        m = compute_metrics_safe(session["decisions"], T=None, baseline_s=None, rt_max=RT_MAX_S)
        per_session.append(m)
    return per_session, surrogate


def summarize(per_session: list[dict], metric: str) -> dict[str, float | None]:
    """mean/std/min/max across sessions for one metric, ignoring Nones."""
    values = [s[metric] for s in per_session if s.get(metric) is not None]
    if not values:
        return {"mean": None, "std": None, "min": None, "max": None}
    arr = np.array(values, dtype=float)
    return {"mean": float(arr.mean()), "std": float(arr.std()), "min": float(arr.min()), "max": float(arr.max())}


def jsd(p: dict[str, float], q: dict[str, float], eps: float = 1e-10) -> float:
    """Jensen-Shannon divergence (log base 2) between two probability
    dicts over the same keys, per the task spec's exact formula."""
    keys = p.keys()
    m = {k: 0.5 * (p[k] + q[k]) for k in keys}

    def kl(a: dict, b: dict) -> float:
        return sum(a[k] * math.log2((a[k] + eps) / (b[k] + eps)) for k in keys)

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def compute_S(sessions: list[dict], surrogate: MarkovSurrogateSC) -> list[float]:
    """Part C: session_S = mean over items of (1 - sqrt(JSD(surrogate_probs,
    reference))), where reference is the same (already Laplace-smoothed)
    row the surrogate itself samples from - see module docstring for why
    this is ~1.0 by construction for the aggregate persona."""
    session_scores = []
    for session in sessions:
        item_scores = []
        for d in session["decisions"]:
            if d.get("actor_type") != "human":
                continue
            probs = d["surrogate_probs"]
            ai_action = None
            # Find the paired ai_evaluated event for this interaction to know
            # which reference row applies.
            for other in session["decisions"]:
                if other["interaction_id"] == d["interaction_id"] and other["actor_type"] == "ai":
                    raw = other["payload"]["ai_decision"]
                    ai_action = {"Accepted": "ai_accept", "Rejected": "ai_reject",
                                 "Flagged for verification": "ai_flag"}[raw]
                    break
            reference = surrogate.transition_matrix.get(ai_action)
            if reference is None:
                continue
            item_s = 1.0 - math.sqrt(max(0.0, jsd(probs, reference)))
            item_scores.append(item_s)
        session_scores.append(float(np.mean(item_scores)) if item_scores else None)
    return session_scores


def per_operator_comparison() -> list[dict]:
    """Part D: real per-operator accept rate vs. 5 surrogate sessions run
    with that operator's own persona."""
    data = json.loads(Path(REAL_DATA_PATH).read_text(encoding="utf-8"))
    real_by_op: dict[int, list[bool]] = {}
    for session in data["logs"]:
        for d in session.get("decisions") or []:
            if d.get("action") != "operator_verified":
                continue
            op_id = (d.get("payload") or {}).get("op_id")
            real_by_op.setdefault(op_id, []).append(bool(d.get("correct")))

    rows = []
    for op_id in sorted(real_by_op):
        real_labels = real_by_op[op_id]
        if len(real_labels) < 20:
            continue
        real_tr = sum(real_labels) / len(real_labels)

        per_session, _ = surrogate_batch_metrics(persona=str(op_id), seed=100 + op_id, n_sessions=5, n_items=32)
        tr_values = [s["Tr"] for s in per_session if s.get("Tr") is not None]
        surr_mean = float(np.mean(tr_values)) if tr_values else None
        surr_std = float(np.std(tr_values)) if tr_values else None

        rows.append({
            "op": op_id, "real_tr": real_tr, "surr_mean": surr_mean, "surr_std": surr_std,
            "n_real": len(real_labels),
            "delta": (surr_mean - real_tr) if surr_mean is not None else None,
        })
    return rows


def fmt(v: float | None, width: int = 6, pct: bool = False) -> str:
    if v is None:
        return "N/A".rjust(width)
    return f"{v:.1%}".rjust(width) if pct else f"{v:.3f}".rjust(width)


def main() -> None:
    print(f"=== PART A: Real pilot baseline (n=164) ===")
    a = real_baseline()
    print(f"  Metric  | Value")
    print(f"  Tr      | {fmt(a['Tr'])}")
    print(f"  HCL     | {fmt(a['HCL'])}")
    print(f"  EL      | {fmt(a['EL'])}  ({a['EL_note']})")
    print(f"  A       | {fmt(a['A'])}" + (f"  ({a['A_note']})" if a['A_note'] else ""))
    print(f"  F       | {fmt(a['F'])}")
    print(f"  S       | N/A  ({a['S_note']})")
    print()

    print("=== PART B: Surrogate sessions (n=20 x 164 items, aggregate persona) ===")
    per_session, agg_surrogate = surrogate_batch_metrics(persona="aggregate", seed=42, n_sessions=20, n_items=164)
    print(f"  Metric  | {'Mean':>8} | {'Std':>8} | {'Min':>8} | {'Max':>8}")
    b_summary = {}
    for metric in ["Tr", "HCL", "EL", "A", "F"]:
        s = summarize(per_session, metric)
        b_summary[metric] = s
        print(f"  {metric:<7} | {fmt(s['mean'], 8)} | {fmt(s['std'], 8)} | {fmt(s['min'], 8)} | {fmt(s['max'], 8)}")
    print()

    print("=== PART C: Surrogate Similarity S ===")
    # Re-generate the same 20 sessions (fresh instance/seed) since Part B's
    # compute_metrics_safe() consumed session dicts but didn't keep them.
    surrogate_c = MarkovSurrogateSC(model_path=MODEL_PATH, persona="aggregate", seed=42)
    sessions_c = surrogate_c.generate_batch(n_sessions=20, n_items=164, rt_max_s=RT_MAX_S, baseline_s=None)
    s_scores = compute_S(sessions_c, surrogate_c)
    valid_s = [s for s in s_scores if s is not None]
    mean_s = float(np.mean(valid_s)) if valid_s else None
    std_s = float(np.std(valid_s)) if valid_s else None
    print(f"  Mean S across {len(valid_s)} sessions: {fmt(mean_s).strip()} ± {fmt(std_s).strip()}")
    print("  Expected range: 0.85-1.0 for aggregate persona (by construction - see module docstring)")
    print()

    print("=== PART D: Per-operator Tr comparison ===")
    rows = per_operator_comparison()
    print(f"  {'Op':<4} | {'Real Tr':>8} | {'Surrogate Tr (mean±std)':>26} | {'n_real':>6} | {'Delta':>8}")
    for r in rows:
        surr_str = f"{fmt(r['surr_mean']).strip()}±{fmt(r['surr_std']).strip()}" if r['surr_mean'] is not None else "N/A"
        print(f"  {r['op']:<4} | {fmt(r['real_tr'])} | {surr_str:>26} | {r['n_real']:>6} | {fmt(r['delta'])}")
    print()

    print("--- Delta summary (B vs A) ---")
    print(f"  {'Metric':<7} | {'Real':>8} | {'Surrogate mean':>15} | {'Delta abs':>10} | {'Delta %':>8}")
    for metric in ["Tr", "HCL", "F"]:
        real_v = a.get(metric)
        surr_v = b_summary[metric]["mean"]
        if real_v is None or surr_v is None:
            continue
        delta_abs = surr_v - real_v
        delta_pct = (delta_abs / real_v * 100) if real_v else None
        pct_str = f"{delta_pct:+.1f}%" if delta_pct is not None else "N/A"
        print(f"  {metric:<7} | {real_v:>8.3f} | {surr_v:>15.3f} | {delta_abs:>+10.3f} | {pct_str:>8}")
    print("  (EL/A/S omitted - not available on both sides, see notes above)")


if __name__ == "__main__":
    main()
