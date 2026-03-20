"""
Hardening tests for metrics_core.

Covers the 5 silent-default bugs fixed in interaction_metrics, latency, human_rt,
and outcome_metrics, plus backward-compatibility of the public API.

Each test is self-contained with inline fixtures — no external files required.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Inline event-builder helpers (pilot_apps contract)
# ---------------------------------------------------------------------------

def _app(user_id="u1", ts="2026-02-02T08:00:00+00:00"):
    return {"event_type": "application_created", "user_id": user_id, "timestamp": ts}


def _ai(agent_id="model-v1", ts="2026-02-02T08:00:01+00:00", latency_ms=250.0):
    return {"event_type": "ai_evaluated", "agent_id": agent_id, "timestamp": ts,
            "latency_ms": latency_ms}


def _op(user_id="u1", ts="2026-02-02T08:00:30+00:00", duration_s=29.0, is_correct=True):
    return {"event_type": "operator_verified", "user_id": user_id, "timestamp": ts,
            "duration_s": duration_s, "is_correct": is_correct}


# ---------------------------------------------------------------------------
# BUG 1 — nanosecond ISO-8601 timestamps
# ---------------------------------------------------------------------------

def test_nanosecond_timestamp_parses_without_error():
    from metrics_core.models import _parse_ts
    # Python's fromisoformat rejects more than 6 fractional digits.
    # The fix strips sub-microsecond digits before calling fromisoformat.
    ts_ns = "2026-02-02T08:00:00.000000729+00:00"
    result = _parse_ts(ts_ns)
    assert result is not None, "nanosecond ISO string should parse to a datetime"
    assert result.tzinfo is not None, "result must be tz-aware"


# ---------------------------------------------------------------------------
# BUG 2 — EL returns 0.0 silently when baseline is absent
# ---------------------------------------------------------------------------

def test_el_none_when_baseline_missing_single_session():
    from metrics_core import compute_metrics_with_results
    decisions = [
        {"agent": "a1", "actor_type": "ai", "t": 0.0},
        {"agent": "a1", "actor_type": "ai", "t": 10.0},
    ]
    result = compute_metrics_with_results(decisions=decisions)
    el = result["EL"]
    assert el.value is None, "EL must be None when no baseline configured and only one session"
    assert el.warning is not None
    assert "cannot be inferred" in el.warning


def test_el_inferred_from_p95_multi_session():
    from metrics_core import compute_metrics_with_results
    decisions = [
        {"agent": "a1", "actor_type": "ai", "t": 0.0, "latency_ms": 200.0},
        {"agent": "a1", "actor_type": "ai", "t": 50.0, "latency_ms": 200.0},
    ]
    # P95 of [30, 60]: i = 1*0.95 = 0.95 → 30*0.05 + 60*0.95 = 58.5
    result = compute_metrics_with_results(
        decisions=decisions,
        baseline_s=None,
        all_session_times=[30.0, 60.0],
    )
    el = result["EL"]
    assert el.value is not None, "EL should be computed when all_session_times has >=2 entries"
    assert el.inferred is True, "EL.inferred must be True when baseline was auto-derived"


# ---------------------------------------------------------------------------
# BUG 3 — Tr returns 1.0 silently when no labeled events exist
# ---------------------------------------------------------------------------

def test_tr_none_when_no_labeled_events():
    from metrics_core import compute_metrics_with_results
    decisions = [
        {"agent": "op1", "actor_type": "human", "t": 0.0, "duration_s": 20.0},
    ]
    result = compute_metrics_with_results(decisions=decisions)
    tr = result["Tr"]
    assert tr.value is None, "Tr must be None when no decision has a 'correct' label"
    assert tr.warning is not None
    assert "correct" in tr.warning


def test_tr_correct_when_operator_events_present():
    from metrics_core.adapters.pilot_apps import to_decisions
    from metrics_core import compute_metrics_with_results
    events = [
        _app(), _ai(), _op(is_correct=True),
        _app(user_id="u2", ts="2026-02-02T09:00:00+00:00"),
        _ai(ts="2026-02-02T09:00:01+00:00"),
        _op(user_id="u2", ts="2026-02-02T09:00:30+00:00", is_correct=True),
    ]
    decisions = to_decisions(events)
    result = compute_metrics_with_results(decisions=decisions)
    tr = result["Tr"]
    assert tr.value is not None, "Tr should be a float when operator_verified events are present"
    assert isinstance(tr.value, float)
    assert tr.value == 1.0, "all correct=True → Tr == 1.0"


# ---------------------------------------------------------------------------
# BUG 5 — HCL falls back to rt_max (worst case) when no human RT data
# ---------------------------------------------------------------------------

def test_hcl_none_when_no_human_rt_data():
    from metrics_core import compute_metrics_with_results
    # AI-only events with no latency or duration fields at all
    decisions = [
        {"agent": "model-v1", "actor_type": "ai", "t": 0.0},
        {"agent": "model-v1", "actor_type": "ai", "t": 5.0},
    ]
    result = compute_metrics_with_results(decisions=decisions)
    hcl = result["HCL"]
    assert hcl.value is None, "HCL must be None when no timing data is present"
    assert hcl.warning is not None


def test_hcl_fallback_duration_s_used_for_operator():
    from metrics_core.adapters.pilot_apps import to_decisions
    from metrics_core import compute_metrics_with_results
    events = [_app(), _ai(), _op(duration_s=25.0, is_correct=True)]
    decisions = to_decisions(events)
    # With rt_max=30s: HCL = clip(1 - 25/30) ≈ 0.167
    result = compute_metrics_with_results(decisions=decisions, rt_max=30.0)
    hcl = result["HCL"]
    assert hcl.value is not None, "HCL should use operator duration_s when present"
    assert 0.0 < hcl.value < 1.0
    assert abs(hcl.value - (1.0 - 25.0 / 30.0)) < 0.001


# ---------------------------------------------------------------------------
# BUG 4 — Adaptability returns 0.0 silently when events are unlabeled
# ---------------------------------------------------------------------------

def test_adaptability_none_when_under_4_events():
    from metrics_core import compute_metrics_with_results
    # 3 agent rows, none with a 'correct' label → both windows have no labeled events
    decisions = [
        {"agent": "a1", "actor_type": "ai", "t": 0.0},
        {"agent": "a1", "actor_type": "ai", "t": 5.0},
        {"agent": "a1", "actor_type": "ai", "t": 10.0},
    ]
    result = compute_metrics_with_results(decisions=decisions)
    a = result["A"]
    assert a.value is None, "A must be None when no labeled events exist in either window"
    assert a.warning is not None
    assert "no labeled events" in a.warning


# ---------------------------------------------------------------------------
# Outcome metrics — precision None when no TP/FP
# ---------------------------------------------------------------------------

def test_outcome_precision_none_when_no_tp_fp():
    from metrics_core import OutcomeMetrics
    # Events with no prediction / ground_truth / result_label fields
    # → _derive_confusion returns all-zero dict → denom=0 → value=None
    data = [{}, {}]
    result = OutcomeMetrics.Effectiveness.calculate_precision(data)
    assert result.value is None, "precision must be None when there are no TP or FP events"


# ---------------------------------------------------------------------------
# Latency — actor_type filter takes precedence over action name
# ---------------------------------------------------------------------------

def test_latency_actor_type_filter_over_action_name():
    from metrics_core import latency_percentiles_by
    logs_root = {
        "logs": [
            {
                "ai_model_version": "v1",
                "decisions": [
                    # actor_type=ai with custom action not in hardcoded set → INCLUDED
                    {"actor_type": "ai", "action": "custom_action", "latency_ms": 300.0},
                    # actor_type=human with action in hardcoded set → EXCLUDED
                    {"actor_type": "human", "action": "classify", "latency_ms": 100.0},
                    # no actor_type, action in hardcoded set → INCLUDED via fallback
                    {"action": "classify", "latency_ms": 200.0},
                ],
            }
        ]
    }
    result = latency_percentiles_by(logs_root)
    assert result["counts"].get("v1", 0) == 2, (
        "should count actor_type=ai event and fallback-classify event; "
        "human event with action=classify must be excluded"
    )
    # Median of [200, 300] = 250ms
    assert result["data"][0][0] == 250.0


# ---------------------------------------------------------------------------
# Human RT — SLA inferred from P95 when not configured
# ---------------------------------------------------------------------------

def test_human_rt_sla_inferred_from_p95():
    from metrics_core import human_response_percentiles_by
    rts = [5, 8, 10, 12, 15, 18, 20, 22, 25, 30]
    logs_root = {
        "logs": [
            {
                "pilot_tag": "cohort_A",
                "decisions": [
                    {"actor_type": "human", "duration_s": float(v)} for v in rts
                ],
            }
        ]
    }
    result = human_response_percentiles_by(logs_root)
    assert result["sla_source"] == "inferred_p95"
    assert result["sla_s_inferred"] is True
    assert result["sla_s"] is not None
    # P95 of [5,8,10,12,15,18,20,22,25,30]:
    # n=10, i = 9*0.95 = 8.55, lo=8, hi=9
    # = 25*(1-0.55) + 30*0.55 = 11.25 + 16.5 = 27.75
    assert abs(result["sla_s"] - 27.75) < 0.01


# ---------------------------------------------------------------------------
# Backward compatibility — compute_metrics() returns float|None, not MetricResult
# ---------------------------------------------------------------------------

def test_compute_metrics_backward_compat_returns_floats():
    from metrics_core import compute_metrics
    decisions = [
        {"agent": "a1", "actor_type": "ai", "t": 0.0,  "latency_ms": 200.0, "correct": True},
        {"agent": "a1", "actor_type": "ai", "t": 10.0, "latency_ms": 300.0, "correct": True},
    ]
    result = compute_metrics(decisions=decisions, baseline_s=8.0, rt_max=5.0)
    assert isinstance(result, dict)
    for key, val in result.items():
        assert val is None or isinstance(val, float), (
            f"compute_metrics() must return float|None per key; "
            f"got {type(val).__name__} for key '{key}'"
        )
