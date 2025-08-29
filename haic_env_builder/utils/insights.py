from __future__ import annotations
from typing import Dict, Any, List, Tuple
import math

def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def _rag(value: float, bands: Tuple[float, float], higher_is_better: bool = True) -> Tuple[str, str]:
    """
    Map a value to (emoji, label) given 2 thresholds.
    bands: (yellow_threshold, green_threshold) if higher_is_better
           (green_threshold, yellow_threshold) if lower_is_better
    """
    lo, hi = bands
    v = float(value)
    if higher_is_better:
        if v >= hi:     return ("🟢", "strong")
        if v >= lo:     return ("🟡", "ok")
        return ("🔴", "weak")
    else:
        if v <= lo:     return ("🟢", "low")
        if v <= hi:     return ("🟡", "moderate")
        return ("🔴", "high")

def summarize_run_brief(result: Dict[str, Any]) -> str:
    decs = result.get("decisions", []) or []
    N = len(decs)
    T = 0.0
    if N >= 2:
        try:
            T = float(decs[-1].get("t", 0.0)) - float(decs[0].get("t", 0.0))
        except Exception:
            T = 0.0
    mets = result.get("metrics", {}) or {}
    F  = float(mets.get("F", 0.0))                       # interactions/min
    H  = float(mets.get("HCL", 0.0))                     # 0..1
    Tr = float(mets.get("Tr", 0.0))                      # 0..1 accuracy
    A  = float(mets.get("A", 0.0))                       # relative change
    S  = float(mets.get("S", 0.0))                       # 0..1 similarity
    EL = float(mets.get("EL", 0.0))                      # >=0
    ES = float(mets.get("EfficiencyScore", 0.0))         # 0..1

    # quick counts
    offrole = sum(1 for d in decs if d.get("off_role_action"))
    progress = sum(1 for d in decs if str(d.get("event_type","")).lower() in {"progress","checklist_progress"})
    offrole_rate = (offrole / N) if N > 0 else 0.0

    # headline sentence
    task = result.get("task", "Scenario")
    env  = result.get("environment", "env")
    headline = (
        f"{task} ({env}): {N} actions in ~{T:.1f}s · pace {F:.1f}/min · "
        f"efficiency {ES:.2f} (EL={EL:.2f}) · accuracy {Tr:.2f} · responsiveness {H:.2f}."
    )
    # small add-ons
    add = []
    if A > 0.05: add.append("improving over time")
    elif A < -0.05: add.append("degrading over time")
    if S >= 0.8: add.append("aligned with surrogate")
    elif S <= 0.5: add.append("diverging from surrogate")
    if offrole_rate > 0.1: add.append("frequent off-role actions")
    if progress > 0: add.append(f"{progress} progress ticks")
    if add:
        headline += " " + ("; ".join(add)) + "."

    return headline

def interpret_metrics(metrics: Dict[str, float], *, offrole_rate: float = 0.0, progress_per_sec: float = 0.0) -> List[str]:
    """
    Turn metric values into short, ‘natural’ insights with emojis.
    """
    F  = float(metrics.get("F", 0.0))
    D  = float(metrics.get("D", 0.0))
    H  = float(metrics.get("HCL", 0.0))
    Tr = float(metrics.get("Tr", 0.0))
    A  = float(metrics.get("A", 0.0))
    S  = float(metrics.get("S", 0.0))
    EL = float(metrics.get("EL", 0.0))
    ES = float(metrics.get("EfficiencyScore", 0.0))

    insights: List[str] = []

    # Pace
    pace_emoji, pace_label = _rag(F, (5, 15), higher_is_better=True)    # tweak bands per domain if needed
    insights.append(f"{pace_emoji} **Pace** ({F:.1f}/min): {pace_label} activity level.")

    # Responsiveness
    h_emoji, h_label = _rag(H, (0.6, 0.8), higher_is_better=True)
    insights.append(f"{h_emoji} **Responsiveness** (HCL={H:.2f}): {h_label} reaction speed.")

    # Accuracy
    tr_emoji, tr_label = _rag(Tr, (0.9, 0.97), higher_is_better=True)
    insights.append(f"{tr_emoji} **Accuracy** (Tr={Tr:.2f}): {tr_label} error rate.")

    # Adaptability
    if A >= 0.10:
        insights.append(f"🟢 **Adaptability** (A=+{A:.2f}): learning trend; performance improved late vs early.")
    elif A <= -0.10:
        insights.append(f"🔴 **Adaptability** (A={A:.2f}): degrading trend; watch late-stage mistakes.")
    else:
        insights.append(f"🟡 **Adaptability** (A={A:.2f}): stable; no strong trend.")

    # Surrogate alignment
    s_emoji, s_label = _rag(S, (0.5, 0.8), higher_is_better=True)
    if S >= 0.8:
        insights.append(f"{s_emoji} **Surrogate alignment** (S={S:.2f}): high agreement with the reference policy.")
    elif S <= 0.5:
        insights.append(f"{s_emoji} **Surrogate alignment** (S={S:.2f}): diverging; investigate rationale or labeling.")
    else:
        insights.append(f"{s_emoji} **Surrogate alignment** (S={S:.2f}): partial match; acceptable drift.")

    # Off-role
    or_emoji, or_label = _rag(offrole_rate, (0.05, 0.10), higher_is_better=False)
    insights.append(f"{or_emoji} **Policy conformity** (off-role {offrole_rate:.1%}): {or_label} off-space usage.")

    # Progress signal
    if progress_per_sec > 0:
        insights.append(f"🟢 **Task progress**: {progress_per_sec:.2f} progress ticks/sec observed.")
    else:
        insights.append("🟡 **Task progress**: no explicit progress ticks; relies on final outcomes.")

    # Efficiency composite
    es_emoji, es_label = _rag(ES, (0.6, 0.8), higher_is_better=True)
    insights.append(f"{es_emoji} **Efficiency** (score={ES:.2f}, EL={EL:.2f}): {es_label} overall efficiency.")

    return insights

def derive_aux_rates(result: Dict[str, Any]) -> Dict[str, float]:
    decs = result.get("decisions", []) or []
    N = len(decs)
    offrole = sum(1 for d in decs if d.get("off_role_action"))
    offrole_rate = (offrole / N) if N > 0 else 0.0
    # progress per second
    progress_count = sum(1 for d in decs if str(d.get("event_type","")).lower() in {"progress","checklist_progress"})
    T = 0.0
    if N >= 2:
        try:
            T = float(decs[-1].get("t", 0.0)) - float(decs[0].get("t", 0.0))
        except Exception:
            T = 0.0
    progress_per_sec = (progress_count / T) if T > 0 else 0.0
    return {"offrole_rate": offrole_rate, "progress_per_sec": progress_per_sec}
