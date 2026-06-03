"""
Piece-3 schema contract tests.

Covers: schema_bridge field mapping, nanosecond timestamps, invalid decision
handling, normalize_log_payload envelope unwrapping, compute_from_log warnings
key, validation_warnings in LogIngestResponse, and run_evaluation warnings
propagation into result_data.

All tests run without external services (in-memory SQLite + mocked MinIO).
"""

import sys
import io
import json
import logging
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent

for _p in (PROJECT_ROOT, BACKEND_ROOT):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# ---------------------------------------------------------------------------
# In-memory SQLite engine
# ---------------------------------------------------------------------------

_sqlite_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_sqlite_engine)

# ---------------------------------------------------------------------------
# App + model imports
# ---------------------------------------------------------------------------

from app.utils.database import get_db as real_get_db, Base
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry       # noqa: F401 — registers ORM mapping
from app.models.results import EvaluationResult  # noqa: F401
from app.utils.errors import ErrorEnvelope, ErrorDetail

import app.routers.logs as _logs_mod
import app.routers.evaluate as _evaluate_mod
import app.routers.meta as _meta_mod

from app.routers.meta import router as _meta_router
from app.routers.evaluate import router as _evaluate_router
from app.routers.logs import router as _logs_router
from app.routers.results import router as _results_router

for _tbl in (EvaluationConfig.__table__, LogEntry.__table__, EvaluationResult.__table__):
    _tbl.create(bind=_sqlite_engine, checkfirst=True)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

from app.services.schema_bridge import log_schema_to_session_log, normalize_log_payload
from app.services.metrics_adapter import compute_from_log

# ---------------------------------------------------------------------------
# Minimal test app
# ---------------------------------------------------------------------------


def _make_test_app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(_meta_router,     prefix="/meta")
    _app.include_router(_evaluate_router, prefix="/api/v1/evaluate")
    _app.include_router(_logs_router,     prefix="/api/v1/logs")
    _app.include_router(_results_router,  prefix="/api/v1/results")

    @_app.exception_handler(Exception)
    async def _exc_handler(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, HTTPException):
            raise exc
        return JSONResponse(
            status_code=500,
            content=ErrorEnvelope(
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred.",
                    details={"exception_type": type(exc).__name__},
                )
            ).model_dump(),
        )

    return _app


_test_app = _make_test_app()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session():
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    _test_app.dependency_overrides[real_get_db] = override_get_db

    mock_minio = MagicMock()
    mock_minio.put_object.return_value = None
    monkeypatch.setattr(_logs_mod, "minio_client", mock_minio)
    monkeypatch.setattr(_logs_mod, "MINIO_BUCKET", "test-bucket")

    mock_meta_minio = MagicMock()
    mock_meta_minio.list_buckets.return_value = []
    monkeypatch.setattr(_meta_mod, "get_minio_client", lambda: mock_meta_minio)

    def _fake_run_evaluation(config_id: int) -> None:
        pass

    monkeypatch.setattr(_evaluate_mod, "execute_evaluation", _fake_run_evaluation)

    yield TestClient(_test_app, raise_server_exceptions=False)

    _test_app.dependency_overrides.clear()


def _make_config(db: Session) -> int:
    config = EvaluationConfig(
        application_name="Test App",
        ai_model_name="test-model-v1",
        ai_model_type="classifier",
        metrics=["accuracy"],
        description="piece-3 test",
        config_type="haic_session",
        evaluation_status="pending",
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config.id


# ---------------------------------------------------------------------------
# Tests — schema_bridge unit tests
# ---------------------------------------------------------------------------


def test_log_schema_to_session_log_basic():
    raw = {
        "session_id": "s-basic",
        "user_id": "u-basic",
        "app_version": "2.0.0",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T01:00:00Z",
    }
    session_log, warnings = log_schema_to_session_log(raw)

    assert session_log.session_id == "s-basic"
    assert session_log.app_version == "2.0.0"
    # pilot_tag falls back to app_version when absent
    assert session_log.pilot_tag == "2.0.0"
    # start_time / end_time → session_started_at / session_ended_at
    assert session_log.session_started_at is not None
    assert session_log.session_ended_at is not None
    assert session_log.session_started_at.year == 2026
    assert session_log.session_ended_at.hour == 1


def test_nanosecond_timestamp_in_decision_survives_bridge():
    raw = {
        "session_id": "s-ns",
        "user_id": "u-ns",
        "app_version": "1.0.0",
        "start_time": "2026-02-02T08:00:00Z",
        "end_time": "2026-02-02T09:00:00Z",
        "decisions": [
            {
                "interaction_id": "i-ns-1",
                "timestamp": "2026-02-02T08:00:00.000000729+00:00",  # nanoseconds
                "actor_type": "human",
            }
        ],
    }
    session_log, warnings = log_schema_to_session_log(raw)

    # Decision must parse successfully — no warning for this event
    assert len(session_log.decisions) == 1
    ns_warnings = [w for w in warnings if "i-ns-1" in w]
    assert ns_warnings == [], f"Unexpected warnings for nanosecond decision: {ns_warnings}"


def test_invalid_decision_collected_as_warning_not_exception():
    raw = {
        "session_id": "s-invalid-dec",
        "user_id": "u1",
        "app_version": "1.0.0",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T00:01:00Z",
        "decisions": [
            {
                "interaction_id": "i-bad",
                "actor_type": "robot",  # not in ActorType enum
                "timestamp": "2026-01-01T00:00:01Z",
            },
            {
                "interaction_id": "i-good",
                "actor_type": "human",
                "timestamp": "2026-01-01T00:00:02Z",
            },
        ],
    }
    session_log, warnings = log_schema_to_session_log(raw)

    # Bad decision flagged as a warning — no exception raised
    assert any("i-bad" in w for w in warnings), f"Expected warning for i-bad, got: {warnings}"
    # Good decision still in the session
    assert len(session_log.decisions) == 1
    assert session_log.decisions[0].interaction_id == "i-good"


def test_normalize_log_payload_unwraps_logs_key():
    payload = {
        "logs": [
            {"session_id": "s-a", "app_version": "1.0",
             "start_time": "2026-01-01T00:00:00Z", "end_time": "2026-01-01T01:00:00Z"},
            {"session_id": "s-b", "app_version": "1.0",
             "start_time": "2026-01-01T01:00:00Z", "end_time": "2026-01-01T02:00:00Z"},
        ]
    }
    sessions, warnings = normalize_log_payload(payload)

    assert len(sessions) == 2
    assert sessions[0].session_id == "s-a"
    assert sessions[1].session_id == "s-b"


# ---------------------------------------------------------------------------
# Tests — compute_from_log warnings key
# ---------------------------------------------------------------------------


def test_compute_from_log_warnings_key_present():
    # decision with actor_type but no 'correct' field → Tr warning fires
    log = {
        "session_id": "s-warn",
        "app_version": "1.0",
        "decisions": [
            {
                "interaction_id": "i1",
                "actor_type": "human",
                "timestamp": "2026-01-01T00:00:01Z",
            }
        ],
    }
    result = compute_from_log(log)

    assert "warnings" in result, "'warnings' key must exist in compute_from_log() return"
    tr_warnings = [w for w in result["warnings"] if w.get("metric") == "Tr"]
    assert tr_warnings, f"Expected Tr warning (no labeled events), got: {result['warnings']}"


# ---------------------------------------------------------------------------
# Tests — HTTP endpoint: validation_warnings in LogIngestResponse
# ---------------------------------------------------------------------------


def test_validation_warnings_reach_log_ingest_response(client, db_session):
    config_id = _make_config(db_session)

    # Decision with actor_type but no 'correct' field.
    # compute_from_log → compute_metrics_with_results → Tr + HCL MetricResult warnings
    # → derived["warnings"] → LogIngestResponse.validation_warnings
    log = {
        "session_id": "s-warn-endpoint",
        "user_id": "u1",
        "app_version": "1.0.0",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T00:01:00Z",
        "decisions": [
            {
                "interaction_id": "i1",
                "actor_type": "human",
                "timestamp": "2026-01-01T00:00:01Z",
            }
        ],
    }
    resp = client.post(
        f"/api/v1/logs/register?configuration_id={config_id}",
        json=log,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "validation_warnings" in body
    assert len(body["validation_warnings"]) > 0, (
        f"Expected non-empty validation_warnings, got: {body['validation_warnings']}"
    )


# ---------------------------------------------------------------------------
# Tests — run_evaluation stores warnings in result_data
# ---------------------------------------------------------------------------


def test_evaluate_stores_warnings_in_result_data(monkeypatch):
    import app.services.evaluate as _eval_mod

    # A session with a human decision carrying no 'correct' field.
    # After normalize_log_payload + model_dump, the decision is a valid dict.
    # compute_metrics_with_results → Tr + HCL warnings → result_data["warnings"]
    log_data = [
        {
            "session_id": "s-eval-warn",
            "app_version": "1.0.0",
            "start_time": "2026-01-01T00:00:00Z",
            "end_time": "2026-01-01T00:01:00Z",
            "decisions": [
                {
                    "interaction_id": "i1",
                    "actor_type": "human",
                    "timestamp": "2026-01-01T00:00:01Z",
                }
            ],
        }
    ]
    log_bytes = json.dumps(log_data).encode("utf-8")

    # Mock MinIO: get_object returns the log; put_object captures result writes
    mock_obj = MagicMock()
    mock_obj.read.return_value = log_bytes

    saved_results = []

    def _capture_put(bucket_name, object_name, data, length, content_type):
        if "results" in object_name:
            saved_results.append(json.loads(data.read().decode("utf-8")))

    mock_minio = MagicMock()
    mock_minio.get_object.return_value = mock_obj
    mock_minio.put_object.side_effect = _capture_put

    monkeypatch.setattr(_eval_mod, "minio_client", mock_minio)
    monkeypatch.setenv("MINIO_BUCKET", "test-bucket")

    # Mock SessionLocal: returns a session whose config has a minio_path
    mock_config = MagicMock()
    mock_config.id = 99
    mock_config.minio_path = "99/config_99.json"

    mock_db = MagicMock()
    mock_db.query.return_value.get.return_value = mock_config

    monkeypatch.setattr(_eval_mod, "SessionLocal", MagicMock(return_value=mock_db))

    from app.services.evaluate import run_evaluation
    run_evaluation(99)

    assert saved_results, "run_evaluation did not write any result to MinIO"
    result_data = saved_results[0]
    assert "warnings" in result_data, f"'warnings' key missing from result_data: {result_data.keys()}"
    assert result_data["warnings"] is not None
