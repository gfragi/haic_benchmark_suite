"""
Survey frontend flow tests.
Covers: submit with/without configuration_id, wrong ethics keys → 422,
holistic shows SUS after a linked survey.

Uses in-memory SQLite (same pattern as test_hardening_piece2.py).
"""

import io
import json
import sys
import uuid
import datetime
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from fastapi import FastAPI, Depends
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

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ---------------------------------------------------------------------------
# Model imports
# ---------------------------------------------------------------------------

from app.utils.database import get_db as real_get_db, Base
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry          # noqa: F401 — registers ORM mapping
from app.models.results import EvaluationResult  # noqa: F401

# Create standard tables
for _tbl in (EvaluationConfig.__table__, LogEntry.__table__, EvaluationResult.__table__):
    _tbl.create(bind=_engine, checkfirst=True)

# Survey table: create manually to avoid postgresql.UUID DDL issues on SQLite
with _engine.connect() as _conn:
    _conn.execute(text("""
        CREATE TABLE IF NOT EXISTS surveys (
            survey_id    VARCHAR(36) PRIMARY KEY,
            user_id      TEXT        NOT NULL,
            timestamp    DATETIME    NOT NULL,
            pilot_tag    TEXT        NOT NULL,
            app_version  TEXT,
            ai_model_version TEXT,
            schema_id    VARCHAR(36),
            tam_sus_responses JSON,
            ethics_responses  JSON,
            domain_specific   JSON,
            configuration_id  INTEGER
        )
    """))
    _conn.commit()

# ---------------------------------------------------------------------------
# Router imports
# ---------------------------------------------------------------------------

import app.routers.results as _results_mod
from app.routers.survey import router as _survey_router
from app.routers.results import router as _results_router

# ---------------------------------------------------------------------------
# Test app
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(_survey_router,  prefix="/api/v1/survey")
    _app.include_router(_results_router, prefix="/api/v1/results")
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

    # Mock the module-level minio_client used by results router
    mock_minio = MagicMock()
    monkeypatch.setattr(_results_mod, "minio_client", mock_minio)

    yield TestClient(_test_app)
    _test_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_SUS = {f"sus_q{i}": 4 for i in range(1, 11)}
_VALID_ETHICS = {
    "q_fairness": 4,
    "q_transparency": 4,
    "q_privacy": 4,
    "q_accountability": 4,
    "q_trust": 4,
}

def _survey_body(**overrides):
    body = {
        "user_id": "test-user",
        "pilot_tag": "energy",
        "tam_sus_responses": _VALID_SUS,
        "ethics_responses": _VALID_ETHICS,
    }
    body.update(overrides)
    return body


def _make_config(db: Session) -> int:
    cfg = EvaluationConfig(
        application_name="Survey Test App",
        ai_model_name="test-model",
        ai_model_type="classifier",
        metrics=["accuracy"],
        description="survey test",
        config_type="haic_session",
        evaluation_status="pending",
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg.id


def _make_result(db: Session, config_id: int, minio_path: str = "fake/path.json") -> int:
    r = EvaluationResult(
        configuration_id=config_id,
        result_minio_path=minio_path,
        evaluation_date=datetime.datetime.utcnow(),
        ai_model_version="v1",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r.id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_survey_submit_with_configuration_id(client, db_session):
    config_id = _make_config(db_session)
    resp = client.post("/api/v1/survey", json=_survey_body(configuration_id=config_id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert "survey_id" in body

    # Verify stored with correct configuration_id
    from app.models.survey import Survey
    surveys = db_session.query(Survey).filter(Survey.configuration_id == config_id).all()
    assert len(surveys) == 1


def test_survey_submit_without_configuration_id(client):
    resp = client.post("/api/v1/survey", json=_survey_body())
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_survey_wrong_ethics_keys_returns_422(client):
    body = _survey_body()
    # Replace correct ethics keys with wrong ones (e1..e5)
    body["ethics_responses"] = {f"e{i}": 4 for i in range(1, 6)}
    resp = client.post("/api/v1/survey", json=body)
    assert resp.status_code == 422


def test_holistic_shows_sus_after_linked_survey(client, db_session, monkeypatch):
    import app.routers.results as results_mod

    config_id = _make_config(db_session)
    _make_result(db_session, config_id)

    # Mock MinIO read to return a minimal result payload
    fake_result = {
        "aggregates": {"interaction": {"Tr": 0.8}},
        "warnings": [],
        "fairness": None,
    }
    mock_obj = MagicMock()
    mock_obj.read.return_value = json.dumps(fake_result).encode()
    mock_minio = MagicMock()
    mock_minio.get_object.return_value = mock_obj
    monkeypatch.setattr(results_mod, "minio_client", mock_minio)

    # Submit a linked survey
    resp = client.post("/api/v1/survey", json=_survey_body(configuration_id=config_id))
    assert resp.status_code == 200

    # GET holistic
    resp2 = client.get(f"/api/v1/results/{config_id}/holistic")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["sus"] is not None
    assert data["sus"]["count"] == 1
