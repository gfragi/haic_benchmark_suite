"""
ZIP upload tests.
Covers: merging sessions from multi-file ZIP, invalid-file rejection,
session count in response.

Uses in-memory SQLite + mocked MinIO (same pattern as test_hardening_piece2.py).
"""

import io
import json
import sys
import zipfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ---------------------------------------------------------------------------
# Model + router imports
# ---------------------------------------------------------------------------

from app.utils.database import get_db as real_get_db
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry       # noqa: F401
from app.models.results import EvaluationResult  # noqa: F401

for _tbl in (EvaluationConfig.__table__, LogEntry.__table__, EvaluationResult.__table__):
    _tbl.create(bind=_engine, checkfirst=True)

import app.routers.logs as _logs_mod
from app.routers.logs import router as _logs_router

# ---------------------------------------------------------------------------
# Test app
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(_logs_router, prefix="/api/v1/logs")
    return _app


_test_app = _make_app()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session, monkeypatch):
    def override_db():
        try:
            yield db_session
        finally:
            pass

    _test_app.dependency_overrides[real_get_db] = override_db

    mock_minio = MagicMock()
    mock_minio.put_object.return_value = None
    monkeypatch.setattr(_logs_mod, "minio_client", mock_minio)
    monkeypatch.setattr(_logs_mod, "MINIO_BUCKET", "test-bucket")
    # LogService has its own minio_client instance — mock it too
    monkeypatch.setattr(_logs_mod.log_service, "minio_client", mock_minio)

    yield TestClient(_test_app)
    _test_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "app_version": "1.0",
        "ai_model_version": "model-v1",
        "session_started_at": "2026-01-01T00:00:00Z",
        "session_ended_at": "2026-01-01T00:01:00Z",
        "decisions": [
            {
                "interaction_id": f"{session_id}-1",
                "actor_type": "human",
                "action": "operator_verified",
                "duration_s": 30.0,
                "correct": True,
            }
        ],
    }


def _make_zip(sessions_per_file: list[list[dict]]) -> bytes:
    """Create an in-memory ZIP with one JSON file per element."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for i, sessions in enumerate(sessions_per_file):
            payload = {"logs": sessions} if len(sessions) > 1 else sessions[0]
            zf.writestr(f"session_{i}.json", json.dumps(payload))
    return buf.getvalue()


def _make_config(db_session) -> int:
    cfg = EvaluationConfig(
        application_name="ZIP Test App",
        ai_model_name="test-model",
        ai_model_type="classifier",
        metrics=["accuracy"],
        description="zip test",
        config_type="haic_session",
        evaluation_status="pending",
    )
    db_session.add(cfg)
    db_session.commit()
    db_session.refresh(cfg)
    return cfg.id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_zip_upload_merges_sessions(client, db_session):
    config_id = _make_config(db_session)

    # 3 separate JSON files, each wrapping one session
    zip_bytes = _make_zip([
        [_make_session("s1")],
        [_make_session("s2")],
        [_make_session("s3")],
    ])

    resp = client.post(
        f"/api/v1/logs/upload-zip?configuration_id={config_id}",
        files={"file": ("sessions.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["session_count"] == 3
    assert body["file_count"] == 3


def test_zip_upload_invalid_file_returns_400(client, db_session):
    config_id = _make_config(db_session)

    # Send a plain JSON file to the zip endpoint
    resp = client.post(
        f"/api/v1/logs/upload-zip?configuration_id={config_id}",
        files={"file": ("notazip.json", b'{"session_id": "x"}', "application/json")},
    )
    assert resp.status_code == 400
    assert "zip" in resp.json()["detail"].lower()


def test_zip_upload_triggers_evaluation(client, db_session, monkeypatch):
    """After ZIP upload the config has a minio_path set (evaluation can proceed)."""
    config_id = _make_config(db_session)

    zip_bytes = _make_zip([
        [_make_session("s-a")],
        [_make_session("s-b")],
    ])

    resp = client.post(
        f"/api/v1/logs/upload-zip?configuration_id={config_id}",
        files={"file": ("data.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200
    assert resp.json()["session_count"] == 2

    # Config should now have minio_path set
    cfg = db_session.query(EvaluationConfig).get(config_id)
    assert cfg.minio_path is not None
