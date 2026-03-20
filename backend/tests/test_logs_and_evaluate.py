import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ------------------------------------------------------------------
# Make sure both project root and backend/ are on sys.path
# ------------------------------------------------------------------
BACKEND_ROOT = Path(__file__).resolve().parent.parent      # .../backend
PROJECT_ROOT = BACKEND_ROOT.parent                         # .../haic_benchmark_suite

for p in (PROJECT_ROOT, BACKEND_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from app.main import app
from app.utils.database import get_db as real_get_db, SessionLocal
from app.models.configuration import EvaluationConfig
from app.models.logs import LogEntry  # noqa: F401 (imported so table exists)
from app.models.results import EvaluationResult


# --- DB session fixture -------------------------------------------------------


@pytest.fixture
def db_session():
    """Provide a real DB session for each test (using app's SessionLocal)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Test client fixture ------------------------------------------------------


@pytest.fixture
def client(db_session, monkeypatch):
    """
    FastAPI TestClient with:
    - DB dependency overridden to use SessionLocal
    - MinIO helpers monkeypatched to in-memory store
    - run_evaluation monkeypatched to a lightweight fake
    """
    # ------------------------------------------------------------------
    # Override DB dependency
    # ------------------------------------------------------------------
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[real_get_db] = override_get_db

    # ------------------------------------------------------------------
    # Monkeypatch MinIO helper functions
    # ------------------------------------------------------------------
    from app.utils import minio_utils as minio_mod

    stored_objects: dict[str, dict] = {}

    def fake_put_json(config_id: int, filename: str, data: dict) -> str:
        key = f"{config_id}/{filename}"
        stored_objects[key] = json.loads(json.dumps(data))  # deep copy
        return key

    def fake_get_json(config_id: int, filename: str) -> dict:
        key = f"{config_id}/{filename}"
        return stored_objects[key]

    async def fake_upload_file(file_data: bytes, config_id: int) -> str:
        """
        Fake version of upload_file for /logs/upload:
        just stores the JSON under a deterministic key.
        """
        filename = f"config_{config_id}.json"
        key = f"{config_id}/{filename}"
        try:
            payload = json.loads(file_data.decode("utf-8"))
        except Exception:
            payload = {"raw": file_data.decode("utf-8", errors="ignore")}
        stored_objects[key] = payload
        return key

    monkeypatch.setattr(minio_mod, "put_json", fake_put_json)
    monkeypatch.setattr(minio_mod, "get_json", fake_get_json)
    monkeypatch.setattr(minio_mod, "upload_file", fake_upload_file)

    # ------------------------------------------------------------------
    # Monkeypatch run_evaluation to avoid real MinIO / heavy logic
    # ------------------------------------------------------------------
    from app.services import evaluate as eval_mod

    def fake_run_evaluation(config_id: int) -> None:
        """
        Very lightweight replacement for run_evaluation:
        - marks config as COMPLETED (if status field exists)
        - inserts a dummy EvaluationResult row
        """
        session = SessionLocal()
        try:
            config = session.get(EvaluationConfig, config_id)
            if not config:
                return

            # Mark as completed if your model supports it
            if hasattr(EvaluationConfig, "STATUS_COMPLETED"):
                config.evaluation_status = EvaluationConfig.STATUS_COMPLETED

            # Insert a dummy result
            result = EvaluationResult(
                configuration_id=config_id,
                result_minio_path="dummy/result.json",
                app_version=getattr(config, "app_version", None),
                ai_model_version=getattr(config, "ai_model_name", None),
            )
            session.add(config)
            session.add(result)
            session.commit()
        finally:
            session.close()

    monkeypatch.setattr(eval_mod, "run_evaluation", fake_run_evaluation)

    return TestClient(app)


# --- Helper functions ---------------------------------------------------------


def create_config_direct(db_session) -> int:
    """
    Create an EvaluationConfig directly in the DB and return its ID.
    This avoids depending on any specific API route path.
    """
    config = EvaluationConfig(
        application_name="XR Safety Assistant",
        ai_model_name="xr-safety-detector-v2",
        ai_model_type="vision-transformer",
        metrics=["accuracy", "precision", "recall", "human_effort"],
        description="XR safety pilot test run",
        config_type="haic_session",
        evaluation_status="pending",
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)
    return config.id


def example_log(session_id: str) -> dict:
    """Return a minimal valid log payload for LogSchema."""
    return {
        "session_id": session_id,
        "user_id": "user-test",
        "ai_model_version": "2.0.0",
        "app_version": "1.0.0",
        "start_time": "2025-11-28T22:20:35.000Z",
        "end_time": "2025-11-28T22:25:35.000Z",
        "interaction_data": {
            "image_id": "img-1",
            "presentation_time": "2025-11-28T22:20:40.000Z",
            "validation_data": {
                "ai_detection_results": "OK",
                "confidence_scores": {"class_A": 0.9},
                "validation_results": "OK",
                "confidence_level": 0.8,
                "processing_time_seconds": 4.5,
                "validation_time": "2025-11-28T22:20:45.000Z",
                "system_metrics": {
                    "accuracy": 0.85,
                    "precision": 0.88,
                    "recall": 0.80,
                },
            },
            "review_data": {
                "review_time_seconds": 10,
                "detections_confirmed": 10,
                "false_positives": 1,
                "false_negatives": 0,
                "time_spent_on_corrections_seconds": 5,
                "human_confirmation_rate": 0.8,
            },
            "application_id": "app-1",
            "submission_time": "2025-11-28T22:21:05.000Z",
            "load_generation_data": [],
            "alert_data": None,
        },
        "retrain_events": [],
        "performance_infrastructure": {
            "hardware_specifications": "CPU/GPU info",
            "software_stack": "Python 3.11, FastAPI",
            "network_conditions": "local",
        },
        "performance_logs": {
            "processing_time_seconds": {"pipeline": 4.5},
            "resource_utilization": {"cpu": 0.65},
            "human_effort_seconds": {"annotator": 40},
        },
        "ai_model_data": {
            "ai_model_name": "xr-safety-detector-v2",
            "training_data": "internal",
            "ai_model_size": "1B",
            "inference_time_seconds": 0.22,
            "deployment_details": "docker",
        },
        "decisions": [
            {
                "t": 0,
                "agent": "annotator",
                "actor_type": "human",
                "action": "inspect",
                "duration_s": 2.5,
                "correct": True,
            }
        ],
    }


# --- Tests --------------------------------------------------------------------


def test_upload_log_and_evaluate(client: TestClient, db_session):
    """
    Full walkthrough for the file-upload ingestion path:
    1. Create config (direct DB insert)
    2. Upload log file
    3. Trigger evaluation
    4. Fetch results and check basic properties
    """
    config_id = create_config_direct(db_session)

    # 1) Prepare a log and send it as a "file"
    log_payload = example_log("upload-session-001")
    file_content = json.dumps(log_payload).encode("utf-8")

    resp = client.post(
        f"/api/v1/logs/upload?configuration_id={config_id}",
        files={"file": ("log_upload.json", file_content, "application/json")},
    )
    assert resp.status_code == 200, resp.text

    # 2) Trigger evaluation
    resp = client.post(f"/api/v1/evaluate/{config_id}")
    assert resp.status_code == 200, resp.text
    assert "Evaluation started" in resp.json()["detail"]

    # 3) Fetch results
    resp = client.get(f"/api/v1/results/{config_id}")
    assert resp.status_code == 200, resp.text
    results = resp.json()

    assert isinstance(results, list)
    assert len(results) >= 1

    first = results[0]
    assert "id" in first or "result_minio_path" in first


def test_register_log_and_evaluate(client: TestClient, db_session):
    """
    Full walkthrough for the JSON-register ingestion path:
    1. Create config (direct DB insert)
    2. POST /logs/register with JSON body (twice)
    3. Trigger evaluation
    4. Fetch results and verify at least one result exists
    """
    config_id = create_config_direct(db_session)

    # 1) Register two logs under the same configuration_id
    log1 = example_log("register-session-001")
    log2 = example_log("register-session-002")

    for log_payload in (log1, log2):
        resp = client.post(
            f"/api/v1/logs/register?configuration_id={config_id}",
            json=log_payload,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["detail"] == "Registered log."
        assert "minio_paths" in body or "minio_path" in body
        assert "derived" in body

    # 2) Trigger evaluation
    resp = client.post(f"/api/v1/evaluate/{config_id}")
    assert resp.status_code == 200, resp.text
    assert "Evaluation started" in resp.json()["detail"]

    # 3) Fetch aggregated results
    resp = client.get(f"/api/v1/results/{config_id}")
    assert resp.status_code == 200, resp.text
    results = resp.json()

    assert isinstance(results, list)
    assert len(results) >= 1

    first = results[0]
    assert "id" in first or "result_minio_path" in first
