# app/services/metrics_adapter.py

from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional

from metrics_core.interaction_metrics import compute_metrics_with_results
from metrics_core.schema import MetricResult
from metrics_core.outcome_metrics import Metrics as M

Number = float | int


def _as_sessions(log: Any) -> List[Dict[str, Any]]:
    """Accept a single session dict or a list of session dicts."""
    if isinstance(log, list):
        return [x for x in log if isinstance(x, dict)]
    if isinstance(log, dict):
        return [log]
    return []


def _mean(vals: Iterable[Number]) -> Optional[float]:
    nums = [float(v) for v in vals if isinstance(v, (int, float))]
    return (sum(nums) / len(nums)) if nums else None


def _safe_div(a: Number, b: Number) -> Optional[float]:
    try:
        a = float(a); b = float(b)
        return a / b if b != 0 else None
    except Exception:
        return None


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def compute_from_log(
    log: Any,
    *,
    rt_max: float = 5.0,          # cap for efficiency normalization
    baseline_s: Optional[float] = None,  # reserved (e.g., Human Effort Saved)
    all_session_times: list[float] | None = None,
) -> Dict[str, Any]:
    """
    Returns:
      {
        "by_metric": {<flat metrics, raw>},
        "by_pillar": {<normalized, higher-is-better>},
        "interaction": {F, D, HCL, Tr, A, S, EL}
      }
    """
    sessions = _as_sessions(log)

    # ----------------- Extract from your nested schema -----------------
    accs, precs, recs = [], [], []
    proc_times, confidences = [], []
    fps, fns, det_conf, corr_time = [], [], [], []
    interaction_blocks = []
    all_decisions = []

    for s in sessions:
        idata = (s.get("interaction_data") or {})
        v = idata.get("validation_data") or {}
        r = idata.get("review_data") or {}

        sysm = v.get("system_metrics") or {}
        if isinstance(sysm.get("accuracy"), (int, float)):  accs.append(sysm["accuracy"])
        if isinstance(sysm.get("precision"), (int, float)): precs.append(sysm["precision"])
        if isinstance(sysm.get("recall"), (int, float)):    recs.append(sysm["recall"])

        if isinstance(v.get("processing_time_seconds"), (int, float)):
            proc_times.append(v["processing_time_seconds"])

        if isinstance(v.get("confidence_level"), (int, float)):
            confidences.append(v["confidence_level"])

        if isinstance(r.get("false_positives"), (int, float)):          fps.append(r["false_positives"])
        if isinstance(r.get("false_negatives"), (int, float)):          fns.append(r["false_negatives"])
        if isinstance(r.get("detections_confirmed"), (int, float)):     det_conf.append(r["detections_confirmed"])
        if isinstance(r.get("time_spent_on_corrections_seconds"), (int, float)):
            corr_time.append(r["time_spent_on_corrections_seconds"])

        # for legacy M.* calls that expect interaction_data
        interaction_blocks.append(idata)

        # collect decisions for core HAIC
        ds = s.get("decisions")
        if isinstance(ds, list):
            all_decisions.extend(ds)

    # ----------------- by_metric (raw values, None if missing) -----------------
    by_metric: Dict[str, Optional[float]] = {}

    # Effectiveness
    by_metric["Prediction Accuracy"]   = _mean(accs)
    by_metric["Precision"]             = _mean(precs)
    by_metric["Recall"]                = _mean(recs)
    by_metric["Overall System Accuracy"] = by_metric["Prediction Accuracy"]  # keep same scale [0,1]
    # leave as None (no inputs/formula yet)
    by_metric["Model Improvement Rate"] = None

    # Efficiency (raw)
    by_metric["Response Time"]         = _mean(proc_times)   # seconds
    by_metric["Task Completion Time"]  = None
    # Error Reduction Rate = 1 - (fp + fn) / (dc + fp + fn)
    err_rates = []
    for fp, fn, dc in zip(fps, fns, det_conf):
        denom = (dc or 0) + (fp or 0) + (fn or 0)
        if denom > 0:
            err_rates.append(1.0 - float(fp + fn) / float(denom))
    by_metric["Error Reduction Rate"]  = _mean(err_rates)

    # Resource / Teaching / Knowledge / Correction
    by_metric["Resource Utilization"]  = None
    by_metric["Teaching Efficiency"]   = None
    by_metric["Knowledge Retention"]   = None
    # Correction Efficiency = detections_confirmed / time_spent_on_corrections_seconds
    corr_eff = []
    for dc, t in zip(det_conf, corr_time):
        val = _safe_div(dc, t)  # detections per second
        if val is not None:
            corr_eff.append(val)
    by_metric["Correction Efficiency"]  = _mean(corr_eff)

    # Adaptability & Learning (not present in log)
    by_metric["Feedback Impact"]             = None
    by_metric["Adaptability Score"]          = None
    by_metric["Impact of Corrections"]       = None
    by_metric["Learning Efficiency"]         = None
    by_metric["Objective Fulfillment Rate"]  = None

    # Collaboration & Interaction (some can come from M.* if needed)
    by_metric["AI Assistance Rate"]          = None
    # Use metrics_core for Human-AI Agreement (works with your interaction_data)
    try:
        by_metric["Human-AI Agreement Rate"] = M.CollaborationAndInteraction.calculate_human_ai_agreement_rate(interaction_blocks)
    except Exception:
        by_metric["Human-AI Agreement Rate"] = None
    by_metric["Decision Effectiveness"]      = None
    by_metric["Time to Resolution"]          = None
    by_metric["Human Effort Saved"]          = None  # needs baseline_s (not wired yet)

    # Trust & Safety
    by_metric["Confidence"]                  = _mean(confidences)
    by_metric["Trust Score"]                 = None
    by_metric["Safety Incidents"]            = None
    by_metric["System Reliability"]          = None

    # Robustness
    by_metric["Adversarial Robustness"]      = None
    by_metric["Domain Generalization"]       = None

    # ----------------- Core HAIC (F, D, HCL, Tr, A, S, EL) -----------------
    interaction_results: dict[str, MetricResult] = {}
    if all_decisions:
        try:
            interaction_results = compute_metrics_with_results(
                decisions=all_decisions,
                rt_max=rt_max,
                baseline_s=baseline_s,
                all_session_times=all_session_times,
            )
        except Exception:
            interaction_results = {}

    # Flatten for backward compat
    interaction = {k: v.value for k, v in interaction_results.items()}

    # Collect interaction warnings
    interaction_warnings = [
        {"metric": k, "warning": v.warning}
        for k, v in interaction_results.items()
        if v.warning is not None
    ]

    # ----------------- by_pillar (normalized, higher-is-better) -------------
    # Normalization helpers for pillar scores:
    # - Effectiveness metrics are already in [0,1]
    # - Efficiency: convert Response Time (seconds, lower-is-better) into a score in [0,1]
    rt = by_metric.get("Response Time")
    rt_score = None
    if isinstance(rt, (int, float)) and rt_max and rt_max > 0:
        rt_score = 1.0 - _clamp01(float(rt) / float(rt_max))

    # Build pillar -> list[score or None]
    pillar_components: Dict[str, List[Optional[float]]] = {
        "Effectiveness": [
            by_metric["Prediction Accuracy"],
            by_metric["Precision"],
            by_metric["Recall"],
            by_metric["Overall System Accuracy"],
            by_metric["Model Improvement Rate"],       # stays None unless you implement
        ],
        "Efficiency": [
            rt_score,
            # You can add normalized versions of the raw efficiency metrics later,
            # e.g., norm(Error Reduction Rate), norm(Correction Efficiency), etc.
        ],
        "Adaptability and Learning": [
            by_metric["Feedback Impact"],
            by_metric["Adaptability Score"],
            by_metric["Impact of Corrections"],
            by_metric["Learning Efficiency"],
            by_metric["Objective Fulfillment Rate"],
        ],
        "Collaboration and Interaction": [
            by_metric["AI Assistance Rate"],
            by_metric["Human-AI Agreement Rate"],
            by_metric["Decision Effectiveness"],
            by_metric["Time to Resolution"],
            by_metric["Human Effort Saved"],
        ],
        "Trust and Safety": [
            by_metric["Confidence"],
            by_metric["Trust Score"],
            by_metric["Safety Incidents"],
            by_metric["System Reliability"],
        ],
        "Robustness and Generalization": [
            by_metric["Adversarial Robustness"],
            by_metric["Domain Generalization"],
        ],
    }

    by_pillar: Dict[str, Optional[float]] = {}
    for pillar, scores in pillar_components.items():
        by_pillar[pillar] = _mean([s for s in scores if isinstance(s, (int, float))])

    return {
        "by_metric": by_metric,          # raw values; UI should show N/A for None
        "by_pillar": by_pillar,          # normalized, higher-is-better (currently uses rt_score + effectiveness)
        "interaction": interaction,      # core HAIC minimal set
        "warnings": interaction_warnings,  # list[{metric, warning}]
    }
