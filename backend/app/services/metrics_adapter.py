# app/services/metrics_adapter.py

from __future__ import annotations
import datetime
from typing import Any, Dict, Iterable, List, Optional

from metrics_core.interaction_metrics import compute_metrics_with_results
from metrics_core.schema import MetricResult

Number = float | int

# Known (predicted_key, actual_key) pairs used across pilots' decision payloads
# to express "what the AI proposed" vs "what was finally decided" - there's no
# single universal convention across partners, so each is checked in turn.
# ai_decision/op_decision: Smart Cities / applications pilot (see pilot_guide.md)
# ai_suggested/new_label, model_prediction/new_label: Rok's smart_ticketing pilot
# ai_suggested/final_label: the radiology demo dataset
_AGREEMENT_KEY_PAIRS = [
    ("ai_decision", "op_decision"),
    ("ai_suggested", "new_label"),
    ("model_prediction", "new_label"),
    ("ai_suggested", "final_label"),
]


def _map_surrogate_probs_to_reference(decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For every human decision that carries surrogate_probs, also copy it
    onto "probs".

    interaction_metrics.py's S computation (lines 477-494) has two paths:
    a primary one comparing "probs" (the real-human reference
    distribution) against "surrogate_probs" via KL divergence, and a
    fallback that string-compares "action" against "surrogate_action" -
    which can never match for this surrogate, since "action" is always
    the constant event-type string "operator_verified" while
    surrogate_action holds outcome values like "op_accept". Without this
    mapping, S silently fell through to that broken fallback (S=0.0) or,
    before surrogate_probs/surrogate_action even survived validation,
    to no-signal-at-all (S=None).

    # Surrogate fix: map surrogate_probs -> probs for S metric primary
    # path (interaction_metrics.py:477); avoids broken fallback that
    # compares action vs surrogate_action strings.

    For a Tier 1 surrogate, the surrogate's own emission distribution IS
    the reference distribution for JSD/KL purposes - the same assumption
    scripts/validate_surrogate.py already makes explicitly. Real pilot
    decisions never set surrogate_probs, so this never touches them; AI
    events and human events without surrogate_probs are left untouched
    (S stays None for those, exactly as before).
    """
    mapped = []
    for d in decisions:
        if (
            isinstance(d, dict)
            and d.get("actor_type") == "human"
            and isinstance(d.get("surrogate_probs"), dict)
            and d["surrogate_probs"]
        ):
            d = {**d, "probs": d["surrogate_probs"]}
        mapped.append(d)
    return mapped


def _payload_confidence(payload: Dict[str, Any]) -> Optional[float]:
    """Max class probability from a decision's payload, whichever shape it's in."""
    if not isinstance(payload, dict):
        return None
    probs = payload.get("probs")
    if isinstance(probs, dict) and probs:
        vals = [v for v in probs.values() if isinstance(v, (int, float))]
        if vals:
            return max(vals)
    probabilities = payload.get("probabilities")
    if isinstance(probabilities, list) and probabilities:
        vals = [v for v in probabilities if isinstance(v, (int, float))]
        if vals:
            return max(vals)
    return None


def _derive_extended_from_decisions(decisions: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    """
    Best-effort Confidence / Response Time / Human-AI Agreement Rate signals
    extracted directly from decisions[] payloads, for pilots that don't send
    an explicit interaction_data block. Only used as a fallback in
    compute_from_log() - an explicit interaction_data value always wins over
    this when present.
    """
    confidences: List[float] = []
    response_times: List[float] = []
    agree_total = 0
    agree_matches = 0

    for d in decisions or []:
        if not isinstance(d, dict):
            continue
        payload = d.get("payload") or {}

        if d.get("actor_type") == "ai":
            conf = _payload_confidence(payload)
            if conf is not None:
                confidences.append(conf)
            latency_ms = d.get("latency_ms")
            if isinstance(latency_ms, (int, float)):
                response_times.append(latency_ms / 1000.0)

        for pred_key, actual_key in _AGREEMENT_KEY_PAIRS:
            pred = payload.get(pred_key)
            actual = payload.get(actual_key)
            if pred is not None and actual is not None:
                agree_total += 1
                if str(pred).strip().lower() == str(actual).strip().lower():
                    agree_matches += 1
                break  # first matching convention wins - don't double count

    return {
        "confidence": _mean(confidences),
        "response_time": _mean(response_times),
        "agreement_rate": (agree_matches / agree_total) if agree_total else None,
    }


def _derive_baseline_s(
    sessions: List[Dict[str, Any]],
    configured_baseline: Optional[float],
    all_session_times: Optional[List[float]],
) -> tuple[Optional[float], str]:
    """
    Derive the baseline_s to use for EL computation.

    Priority order:
      1. Explicitly configured value (caller-supplied baseline_s > 0).
      2. meta.task_parameters.baseline_s in any session (partner-supplied in log).
      3. P95 of all_session_times when at least 5 sessions are available.
      4. Cannot derive — EL will be None.

    Returns (baseline_s, source) where source is one of:
      "configured", "session_meta", "p95_inferred (<N> sessions)", "unavailable"
    """
    # Priority 1 — caller-configured
    if configured_baseline is not None and configured_baseline > 0:
        return configured_baseline, "configured"

    # Priority 2 — session meta.task_parameters.baseline_s
    for s in sessions:
        raw = (s.get("meta") or {}).get("task_parameters", {}).get("baseline_s")
        if raw is not None:
            try:
                v = float(raw)
                if v > 0:
                    return v, "session_meta"
            except (TypeError, ValueError):
                pass

    # Priority 3 — P95 of provided session durations (requires ≥5 for reliability)
    if all_session_times and len(all_session_times) >= 5:
        xs = sorted(all_session_times)
        n = len(xs)
        i = 0.95 * (n - 1)
        lo = int(i)
        hi = min(lo + 1, n - 1)
        p95 = xs[lo] + (i - lo) * (xs[hi] - xs[lo])
        if p95 > 0:
            return p95, f"p95_inferred ({n} sessions)"

    return None, "unavailable"


def _derive_rt_max(
    sessions: List[Dict[str, Any]],
    all_human_rts: Optional[List[float]],
) -> tuple[Optional[float], str]:
    """
    Derive the rt_max (human response-time ceiling) used to normalize HCL —
    same P95 auto-derivation pattern as _derive_baseline_s above, applied to
    human response times instead of session durations.

    Priority order:
      1. meta.task_parameters.rt_max / rt_max_s in any session (partner-supplied).
      2. P95 of all_human_rts when at least 5 human response times are
         available across the batch - used as the ceiling itself (not just
         a fallback), since P95 already excludes the extreme top 5% as
         outliers rather than letting the single slowest response set the cap.
      3. Cannot derive - caller's default rt_max is used instead.

    Returns (rt_max, source) where source is "session_meta", "p95_inferred
    (<N> events)", or "default".
    """
    for s in sessions:
        tp = (s.get("meta") or {}).get("task_parameters", {})
        raw = tp.get("rt_max") or tp.get("rt_max_s")
        if raw is not None:
            try:
                v = float(raw)
                if v > 0:
                    return v, "session_meta"
            except (TypeError, ValueError):
                pass

    if all_human_rts and len(all_human_rts) >= 5:
        xs = sorted(all_human_rts)
        n = len(xs)
        i = 0.95 * (n - 1)
        lo = int(i)
        hi = min(lo + 1, n - 1)
        p95 = xs[lo] + (i - lo) * (xs[hi] - xs[lo])
        if p95 > 0:
            return p95, f"p95_inferred ({n} events)"

    return None, "default"


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
    rt_max: float = 30.0,         # cap for efficiency normalization (pilot AI evals run ~14s)
    baseline_s: Optional[float] = None,  # reserved (e.g., Human Effort Saved)
    all_session_times: list[float] | None = None,
    all_human_rts: list[float] | None = None,
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
    agreement_rates = []
    all_decisions = []

    for s in sessions:
        idata = (s.get("interaction_data") or {})
        v = idata.get("validation_data") or {}
        r = idata.get("review_data") or {}

        sysm = v.get("system_metrics") or {}
        if isinstance(sysm.get("accuracy"), (int, float)):  accs.append(sysm["accuracy"])
        if isinstance(sysm.get("precision"), (int, float)): precs.append(sysm["precision"])
        if isinstance(sysm.get("recall"), (int, float)):    recs.append(sysm["recall"])

        if isinstance(r.get("false_positives"), (int, float)):          fps.append(r["false_positives"])
        if isinstance(r.get("false_negatives"), (int, float)):          fns.append(r["false_negatives"])
        if isinstance(r.get("detections_confirmed"), (int, float)):     det_conf.append(r["detections_confirmed"])
        if isinstance(r.get("time_spent_on_corrections_seconds"), (int, float)):
            corr_time.append(r["time_spent_on_corrections_seconds"])

        # collect decisions for core HAIC (and the extended-metrics fallback below)
        ds = s.get("decisions")
        if not isinstance(ds, list):
            ds = []
        # Surrogate fix: map surrogate_probs -> probs for S metric primary
        # path (interaction_metrics.py:477); avoids broken fallback that
        # compares action vs surrogate_action strings.
        all_decisions.extend(_map_surrogate_probs_to_reference(ds))

        # Confidence / Response Time / Human-AI Agreement Rate: prefer an
        # explicit interaction_data value for this session; fall back to
        # deriving directly from decisions[] payloads (see
        # _derive_extended_from_decisions) when the pilot doesn't send one -
        # e.g. Rok's smart_ticketing pilot has no interaction_data at all,
        # but the signal is already present in each decision's payload.
        fallback = _derive_extended_from_decisions(ds)

        if isinstance(v.get("processing_time_seconds"), (int, float)):
            proc_times.append(v["processing_time_seconds"])
        elif fallback["response_time"] is not None:
            proc_times.append(fallback["response_time"])

        if isinstance(v.get("confidence_level"), (int, float)):
            confidences.append(v["confidence_level"])
        elif fallback["confidence"] is not None:
            confidences.append(fallback["confidence"])

        ground_truth, prediction = idata.get("ground_truth"), idata.get("prediction")
        if ground_truth is not None and prediction is not None:
            agreement_rates.append(1.0 if str(ground_truth).strip().lower() == str(prediction).strip().lower() else 0.0)
        elif fallback["agreement_rate"] is not None:
            agreement_rates.append(fallback["agreement_rate"])

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

    # Collaboration & Interaction
    by_metric["AI Assistance Rate"]          = None
    # None (not 0.0) when no session had a determinable ground_truth/
    # prediction pair - the previous implementation returned 0.0 whenever it
    # found zero comparable pairs, making "no data" look identical to "0%
    # agreement".
    by_metric["Human-AI Agreement Rate"]     = _mean(agreement_rates)
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
    # Derive rt_max: session meta > P95 of human response times (≥5 events) >
    # the caller-supplied default.
    derived_rt_max, rt_max_source = _derive_rt_max(sessions, all_human_rts)
    effective_rt_max = derived_rt_max if derived_rt_max is not None else rt_max

    # Derive the best available baseline_s with explicit priority ordering.
    effective_baseline, baseline_source = _derive_baseline_s(
        sessions, baseline_s, all_session_times
    )

    interaction_results: dict[str, MetricResult] = {}
    if all_decisions:
        try:
            interaction_results = compute_metrics_with_results(
                decisions=all_decisions,
                rt_max=effective_rt_max,
                baseline_s=effective_baseline,
                all_session_times=None,  # P95 already handled by _derive_baseline_s
            )
        except Exception:
            interaction_results = {}

    # Post-process EL to annotate derivation source.
    if "EL" in interaction_results:
        el_mr = interaction_results["EL"]
        if baseline_source.startswith("p95_inferred"):
            interaction_results["EL"] = MetricResult(
                metric="EL",
                value=el_mr.value,
                n_events=el_mr.n_events,
                inferred=True,
                warning=(
                    "EL baseline auto-derived from P95 of session durations. "
                    "Upload more sessions or configure baseline_s to improve accuracy."
                ),
            )
        elif baseline_source == "unavailable":
            interaction_results["EL"] = MetricResult(
                metric="EL",
                value=None,
                n_events=0,
                warning=(
                    "EL requires baseline_s. Configure it in your evaluation "
                    "settings or upload 5+ sessions for auto-derivation."
                ),
            )
        # "configured" and "session_meta" → leave MetricResult unchanged

    # Annotate HCL with how its rt_max ceiling was determined.
    if "HCL" in interaction_results:
        hcl_mr = interaction_results["HCL"]
        if hcl_mr.value is not None:
            existing = (hcl_mr.warning + "; ") if hcl_mr.warning else ""
            if rt_max_source.startswith("p95_inferred"):
                interaction_results["HCL"] = MetricResult(
                    metric="HCL",
                    value=hcl_mr.value,
                    n_events=hcl_mr.n_events,
                    inferred=True,
                    warning=existing + (
                        f"HCL rt_max auto-derived as P95 of human response times "
                        f"({effective_rt_max:.1f}s from {rt_max_source}). Upload more "
                        f"sessions or configure meta.task_parameters.rt_max to override."
                    ),
                )
            elif rt_max_source == "default":
                interaction_results["HCL"] = MetricResult(
                    metric="HCL",
                    value=hcl_mr.value,
                    n_events=hcl_mr.n_events,
                    warning=existing + f'HCL computed with default rt_max={rt_max}s. To calibrate for your domain add \u201cmeta\u201d: {{"task_parameters": {{"rt_max": N}}}} to each session, where N is the maximum acceptable human response time in seconds, or upload 5+ sessions for auto-derivation from P95.',
                    inferred=hcl_mr.inferred,
                )
            # "session_meta" \u2192 leave MetricResult unchanged

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
