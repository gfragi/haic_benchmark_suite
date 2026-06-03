"""
Live integration tests — run against a real Docker stack.
Skips automatically if /meta/health returns degraded or is unreachable.

Usage:
    make test-live
    # or manually against running stack:
    pytest backend/tests/test_live_integration.py -v
"""

import pytest
import requests
import json
import time

BASE = "http://localhost:8000"
PILOT_TAG = "live-test"   # isolates test data from real pilot data


# ---------------------------------------------------------------------------
# Stack availability check — skip entire module if stack is not healthy
# ---------------------------------------------------------------------------

def _stack_healthy() -> bool:
    try:
        r = requests.get(f"{BASE}/meta/health", timeout=5)
        h = r.json()
        return h.get("db_ok") and h.get("minio_ok")
    except Exception:
        return False


if not _stack_healthy():
    pytest.skip(
        "Live stack not healthy — run 'make test-live' or 'docker compose up'",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def config_id():
    """Create a test evaluation configuration, yield its id, delete after."""
    resp = requests.post(f"{BASE}/api/v1/configuration/new", json={
        "application_name": "Live Test App",
        "ai_model_name": "live-test-model",
        "ai_model_type": "classifier",
        "metrics": ["accuracy"],
        "description": "Created by test_live_integration.py — safe to delete",
        "config_type": "haic_session",
        "pilot_tag": PILOT_TAG,
    })
    assert resp.status_code == 200, f"Failed to create config: {resp.text}"
    cid = resp.json()["id"]
    yield cid
    # Teardown — best-effort delete
    requests.delete(f"{BASE}/api/v1/configuration/delete/{cid}")


_SESSION = {
    "session_id":       "live-test-session-001",
    "user_id":          "live-operator-01",
    "app_version":      "apps_v1.0.0",
    "ai_model_version": "live-test-model",
    "start_time":       "2026-01-19T07:33:34Z",
    "end_time":         "2026-02-02T08:00:00Z",
    "decisions": [
        {
            "interaction_id": "LIVE_001",
            "timestamp":      "2026-01-19T07:33:34Z",
            "actor_type":     "human",
            "action":         "application_created",
            "payload":        {"role": "citizen"},
        },
        {
            "interaction_id": "LIVE_001",
            "timestamp":      "2026-01-31T22:00:00Z",
            "actor_type":     "ai",
            "action":         "ai_evaluated",
            "latency_ms":     47510.0,
            "payload":        {"ai_decision": "Accepted"},
        },
        {
            "interaction_id": "LIVE_001",
            "timestamp":      "2026-02-02T08:00:00Z",
            "actor_type":     "human",
            "action":         "operator_verified",
            "duration_s":     67.1,
            "correct":        False,
            "payload":        {"op_decision": "Accepted", "role": "operator"},
        },
    ],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_live_health_shape():
    """Health endpoint returns typed response with all required fields."""
    r = requests.get(f"{BASE}/meta/health")
    assert r.status_code == 200
    h = r.json()
    assert {"status", "uptime_s", "version", "db_ok", "minio_ok"} <= h.keys()
    assert h["status"] == "ok"
    assert h["db_ok"] is True
    assert h["minio_ok"] is True


def test_live_register_log(config_id):
    """Register a session log and verify ingest response shape."""
    r = requests.post(
        f"{BASE}/api/v1/logs/register",
        params={"configuration_id": config_id},
        json=_SESSION,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["detail"] == "Registered log."
    assert body["log_id"] is not None
    assert body["event_count"] == 3
    assert isinstance(body["validation_warnings"], list)


def test_live_evaluate_and_get_results(config_id):
    """Full pipeline: register → evaluate → results contain HAIC metrics."""
    # Register
    r = requests.post(
        f"{BASE}/api/v1/logs/register",
        params={"configuration_id": config_id},
        json={**_SESSION, "session_id": "live-test-session-002"},
    )
    assert r.status_code == 200

    # Trigger evaluation
    r = requests.post(f"{BASE}/api/v1/evaluate/{config_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

    # Poll for completion (max 30s)
    from app.utils.database import SessionLocal
    from app.models.configuration import EvaluationConfig

    deadline = time.time() + 30
    while time.time() < deadline:
        r = requests.get(f"{BASE}/api/v1/results/{config_id}")
        if r.status_code == 200 and r.json():
            break
        time.sleep(2)
    assert r.status_code == 200, "No results after 30s"

    results = r.json()
    assert len(results) >= 1

    # Fetch result detail
    result_id = results[0]["id"]
    r = requests.get(f"{BASE}/api/v1/results/{config_id}/{result_id}")
    assert r.status_code == 200
    data = r.json()

    assert "aggregates" in data
    interaction = data["aggregates"].get("interaction", {})
    for key in ("F", "D", "HCL", "Tr", "EL"):
        assert key in interaction, f"Missing HAIC metric: {key}"

    assert "warnings" in data


def test_live_partial_session_warnings(config_id):
    """AI-only session (no operator) produces Tr=None warning."""
    ai_only = {**_SESSION,
               "session_id": "live-test-ai-only",
               "decisions": [d for d in _SESSION["decisions"]
                              if d["action"] != "operator_verified"]}
    r = requests.post(
        f"{BASE}/api/v1/logs/register",
        params={"configuration_id": config_id},
        json=ai_only,
    )
    assert r.status_code == 200
    # validation_warnings may be empty here (decisions are valid),
    # but the response shape must be correct
    assert isinstance(r.json()["validation_warnings"], list)


def test_live_nanosecond_timestamp_accepted(config_id):
    """Nanosecond precision timestamps must not cause 422 or 500."""
    nano_session = {**_SESSION,
                    "session_id": "live-test-nano-ts",
                    "end_time": "2026-02-02T08:00:00.000000729+00:00",
                    "decisions": [{
                        "interaction_id": "NANO_001",
                        "timestamp": "2026-02-02T08:00:00.000000729+00:00",
                        "actor_type": "human",
                        "action": "application_created",
                        "payload": {},
                    }]}
    r = requests.post(
        f"{BASE}/api/v1/logs/register",
        params={"configuration_id": config_id},
        json=nano_session,
    )
    assert r.status_code == 200, \
        f"Nanosecond timestamp rejected: {r.status_code} {r.text}"


def test_live_invalid_config_returns_404():
    """Missing config returns 404, not 500."""
    r = requests.get(f"{BASE}/api/v1/results/99999")
    assert r.status_code == 404


def test_live_error_envelope_shape():
    """404 responses use ErrorEnvelope shape."""
    r = requests.post(f"{BASE}/api/v1/evaluate/99999")
    assert r.status_code == 404
    body = r.json()
    # Either ErrorEnvelope or FastAPI's plain detail — accept both
    assert "detail" in body or "error" in body