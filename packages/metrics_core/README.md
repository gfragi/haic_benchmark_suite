# metrics-core

Shared HAIC metrics package — collab-session metrics, extended metrics, latency, and human response time.

## Setup

The package must be installed (editable) into your active environment before running tests.
From the repo root:

```bash
pip install -e packages/metrics_core
```

If you use the project-level virtual environment:

```bash
source bench-env/bin/activate
pip install -e packages/metrics_core
```

## Running the tests

```bash
# All tests (from repo root)
python -m pytest packages/metrics_core/tests/ -v

# Or from inside the package directory
cd packages/metrics_core
python -m pytest tests/ -v
```

Expected output:

```
12 passed in 0.06s
```

## Test coverage

`tests/test_hardening.py` contains 12 regression tests, one per bug fixed on the hardening branch:

| Test | What it guards |
|---|---|
| `test_nanosecond_timestamp_parses_without_error` | BUG 1 — nanosecond ISO-8601 strings no longer crash `_parse_ts` |
| `test_el_none_when_baseline_missing_single_session` | BUG 2 — `EL` returns `None` (not `0.0`) when no baseline and single session |
| `test_el_inferred_from_p95_multi_session` | BUG 2 — `EL` is auto-derived from P95 of `all_session_times` when ≥2 sessions provided |
| `test_tr_none_when_no_labeled_events` | BUG 3 — `Tr` returns `None` (not `1.0`) when no `correct` field is present |
| `test_tr_correct_when_operator_events_present` | BUG 3 — `Tr` computes correctly when `operator_verified` events supply `is_correct` |
| `test_hcl_none_when_no_human_rt_data` | BUG 5 — `HCL` returns `None` (not `rt_max` worst-case) when no timing data exists |
| `test_hcl_fallback_duration_s_used_for_operator` | BUG 5 — `HCL` uses `duration_s` from operator events when `latency_ms` is absent |
| `test_adaptability_none_when_under_4_events` | BUG 4 — `A` returns `None` (not `0.0`) when no labeled events exist in either window |
| `test_outcome_precision_none_when_no_tp_fp` | `OutcomeMetrics.Effectiveness.calculate_precision` returns `None` when TP+FP = 0 |
| `test_latency_actor_type_filter_over_action_name` | `latency_percentiles_by` uses `actor_type=="ai"` as primary filter; action name is fallback only |
| `test_human_rt_sla_inferred_from_p95` | `human_response_percentiles_by` sets `sla_source="inferred_p95"` when no SLA is configured |
| `test_compute_metrics_backward_compat_returns_floats` | `compute_metrics()` returns `dict[str, float\|None]`, not `MetricResult` objects |

## Dependencies

- Python ≥ 3.10
- pydantic ≥ 2, < 3
- pytest (test-only, not declared in `pyproject.toml` — use the project-level env which already has it)
