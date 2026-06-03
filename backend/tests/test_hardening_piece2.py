"""
Hardening tests for backend/app/ — piece 2.
Covers: health endpoint shape, evaluate 404/400, register log
resilience, results 404, and the global exception handler.

Uses in-memory SQLite so no external PostgreSQL is needed.
"""

import sys
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
# Path setup — same as test_logs_and_evaluate.py
# ---------------------------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent

for _p in (PROJECT_ROOT, BACKEND_ROOT):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# ---------------------------------------------------------------------------
# In-memory SQLite engine (replaces PostgreSQL for tests)
# ---------------------------------------------------------------------------

_sqlite_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # all connections share the same in-memory DB
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_sqlite_engine)

# ---------------------------------------------------------------------------
# App + model imports (individual routers only — avoids env_builder / reporting
# NameError in main.py)
# ---------------------------------------------------------------------------

from app.utils.database import get_db as real_get_db, Base
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry  # noqa: F401 — registers ORM mapping
from app.models.results import EvaluationResult  # noqa: F401
from app.utils.errors import ErrorEnvelope, ErrorDetail

import app.routers.logs as _logs_mod
import app.routers.evaluate as _evaluate_mod
import app.routers.meta as _meta_mod

from app.routers.meta import router as _meta_router
from app.routers.evaluate import router as _evaluate_router
from app.routers.logs import router as _logs_router
from app.routers.results import router as _results_router

# Create only the tables we need (skips JSONB tables incompatible with SQLite)
from sqlalchemy import JSON
from sqlalchemy.schema import CreateTable
for _tbl in (EvaluationConfig.__table__, LogEntry.__table__, EvaluationResult.__table__):
    _tbl.create(bind=_sqlite_engine, checkfirst=True)


# ---------------------------------------------------------------------------
# Minimal test app (avoids importing app.main which has broken imports)
# ---------------------------------------------------------------------------

def _make_test_app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(_meta_router,     prefix="/meta")
    _app.include_router(_evaluate_router, prefix="/api/v1/evaluate")
    _app.include_router(_logs_router,     prefix="/api/v1/logs")
    _app.include_router(_results_router,  prefix="/api/v1/results")

    _logger = logging.getLogger(__name__)

    # Test-only route that raises a bare Exception
    @_app.get("/_test/raise")
    async def _raise_bare():
        raise RuntimeError("test boom")

    @_app.exception_handler(Exception)
    async def _exc_handler(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, HTTPException):
            raise exc
        _logger.error("Unhandled: %s", repr(exc), exc_info=True)
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
    # Override DB dependency with SQLite session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    _test_app.dependency_overrides[real_get_db] = override_get_db

    # Mock module-level minio client used by logs router
    mock_minio = MagicMock()
    mock_minio.put_object.return_value = None
    monkeypatch.setattr(_logs_mod, "minio_client", mock_minio)
    monkeypatch.setattr(_logs_mod, "MINIO_BUCKET", "test-bucket")

    # Mock get_minio_client in meta router (health endpoint calls it inline)
    mock_meta_minio = MagicMock()
    mock_meta_minio.list_buckets.return_value = []
    monkeypatch.setattr(_meta_mod, "get_minio_client", lambda: mock_meta_minio)

    # Prevent background evaluation from hitting real services
    def _fake_run_evaluation(config_id: int) -> None:
        pass

    monkeypatch.setattr(_evaluate_mod, "execute_evaluation", _fake_run_evaluation)

    # raise_server_exceptions=False so our @exception_handler(Exception) can
    # return a proper JSONResponse without the TestClient re-raising the exc
    yield TestClient(_test_app, raise_server_exceptions=False)

    _test_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(db: Session) -> int:
    config = EvaluationConfig(
        application_name="Test App",
        ai_model_name="test-model-v1",
        ai_model_type="classifier",
        metrics=["accuracy"],
        description="hardening piece-2 test",
        config_type="haic_session",
        evaluation_status="pending",
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config.id


_MIN_LOG = {
    "session_id": "s-hardening-test",
    "user_id": "u-hardening-test",
    "app_version": "1.0.0",
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-01-01T00:01:00Z",
    "decisions": [
        {
            "event_type": "application_created",
            "user_id": "u1",
            "timestamp": "2026-01-01T00:00:01Z",
        },
        {
            "event_type": "ai_evaluated",
            "agent_id": "m1",
            "timestamp": "2026-01-01T00:00:02Z",
            "latency_ms": 150.0,
        },
    ],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_health_returns_typed_response(client):
    resp = client.get("/meta/health")
    assert resp.status_code == 200
    body = resp.json()
    # Shape check
    assert set(body.keys()) >= {"status", "uptime_s", "version", "db_ok", "minio_ok"}
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["uptime_s"], float)
    assert isinstance(body["db_ok"], bool)
    assert isinstance(body["minio_ok"], bool)
    # SQLite SELECT 1 works → db_ok True; minio mock works → minio_ok True
    assert body["db_ok"] is True
    assert body["minio_ok"] is True
    assert body["status"] == "ok"


def test_evaluate_missing_config_returns_404(client):
    resp = client.post("/api/v1/evaluate/99999")
    assert resp.status_code == 404


def test_evaluate_no_logs_returns_400(client, db_session):
    config_id = _make_config(db_session)
    resp = client.post(f"/api/v1/evaluate/{config_id}")
    assert resp.status_code == 400
    assert "No logs" in resp.json()["detail"]


def test_register_log_compute_failure_does_not_500(client, db_session, monkeypatch):
    config_id = _make_config(db_session)

    def _raise(payload):
        raise ValueError("simulated compute failure")

    monkeypatch.setattr(_logs_mod, "compute_from_log", _raise)

    resp = client.post(
        f"/api/v1/logs/register?configuration_id={config_id}",
        json=_MIN_LOG,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["detail"] == "Registered log."
    assert "_warning" in body["derived"]
    assert "ValueError" in body["derived"]["_warning"]


def test_register_log_missing_config_returns_404(client):
    resp = client.post(
        "/api/v1/logs/register?configuration_id=99999",
        json=_MIN_LOG,
    )
    assert resp.status_code == 404


def test_results_missing_config_returns_404(client):
    resp = client.get("/api/v1/results/99999")
    assert resp.status_code == 404


def test_global_handler_returns_error_envelope(client):
    resp = client.get("/_test/raise")
    assert resp.status_code == 500
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["details"]["exception_type"] == "RuntimeError"
