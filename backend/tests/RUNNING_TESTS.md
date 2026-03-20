# Running the backend tests

## Prerequisites

```bash
cd haic_benchmark_suite/backend
pip install -r requirements.txt
```

The hardening tests (`test_hardening_piece2.py`) use **in-memory SQLite** and
**mocked MinIO / MinIO client**, so they run without any external services.

> **Note:** `httpx` must be `==0.26.0` (pinned in `requirements.txt`).
> If you see `TypeError: Client.__init__() got an unexpected keyword argument 'app'`
> run `pip install "httpx==0.26.0"` — this is a starlette 0.36.3 / httpx 0.28
> incompatibility.

---

## Run all tests

```bash
# from backend/
pytest
```

`pytest.ini` sets `testpaths = tests` and `--verbose --tb=short` by default.

---

## Run only the hardening tests

```bash
pytest tests/test_hardening_piece2.py
```

### Piece-2 test coverage

| Test | What it checks |
|---|---|
| `test_health_returns_typed_response` | `GET /meta/health` returns `HealthResponse` shape; `db_ok` and `minio_ok` are booleans |
| `test_evaluate_missing_config_returns_404` | `POST /api/v1/evaluate/99999` → 404 when config doesn't exist |
| `test_evaluate_no_logs_returns_400` | `POST /api/v1/evaluate/{id}` → 400 when config exists but has no logs |
| `test_register_log_compute_failure_does_not_500` | `compute_from_log` raising doesn't crash the endpoint; `_warning` appears in `derived` |
| `test_register_log_missing_config_returns_404` | `POST /api/v1/logs/register` → 404 when config_id doesn't exist |
| `test_results_missing_config_returns_404` | `GET /api/v1/results/99999` → 404 when no results exist |
| `test_global_handler_returns_error_envelope` | Bare `RuntimeError` returns 500 with `{"error": {"code": "INTERNAL_ERROR", ...}}` shape |

---

## Run a single test

```bash
pytest tests/test_hardening_piece2.py::test_global_handler_returns_error_envelope
```

---

## Run only the Piece-3 schema tests

```bash
pytest tests/test_piece3_schema.py
```

### Piece-3 test coverage

| Test | What it checks |
|---|---|
| `test_log_schema_to_session_log_basic` | `start_time/end_time` → `session_started_at/session_ended_at`; `pilot_tag` falls back to `app_version` |
| `test_nanosecond_timestamp_in_decision_survives_bridge` | 9-digit fractional-second timestamps parse without warnings |
| `test_invalid_decision_collected_as_warning_not_exception` | Invalid `actor_type` → warning collected; valid sibling decision kept in session |
| `test_normalize_log_payload_unwraps_logs_key` | `{"logs": [...]}` envelope is unwrapped to a list of `SessionLog` objects |
| `test_compute_from_log_warnings_key_present` | `compute_from_log()` return always has `"warnings"` key; Tr warning fires when no `correct` field |
| `test_validation_warnings_reach_log_ingest_response` | MetricResult warnings (Tr/HCL/A/EL) surface in `LogIngestResponse.validation_warnings` |
| `test_evaluate_stores_warnings_in_result_data` | `run_evaluation()` writes `"warnings"` into the MinIO result JSON |

---

## Other test files

| File | Dependencies | Notes |
|---|---|---|
| `test_data_evaluation.py` | None | Pure unit tests; always runnable |
| `test_logs_and_evaluate.py` | PostgreSQL + MinIO | Integration tests; require full stack |
| `test_config.py` | PostgreSQL + `haic_env_builder` package | Fails to collect without env_builder installed |
| `test_evaluation_result.py` | PostgreSQL + `haic_env_builder` package | Same as above |
| `test_evaluate.py` | None | Stub test; uses incorrect `http.client` import |

Run only the tests that are safe to run without infrastructure:

```bash
pytest tests/test_data_evaluation.py tests/test_hardening_piece2.py tests/test_piece3_schema.py
```
