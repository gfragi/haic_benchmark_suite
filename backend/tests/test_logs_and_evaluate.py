import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ------------------------------------------------------------------
# Ensure backend/ is on sys.path so 'app' package is importable
# ------------------------------------------------------------------
BACKEND_ROOT = Path(__file__).resolve().parent.parent  # backend/
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app
from app.utils.database import get_db, Base

# --- Test DB setup (SQLite) ---

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_logs.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a SQLAlchemy session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session, monkeypatch):
    """
    FastAPI TestClient with:
    - DB dependency overridden to use the test session
    - MinIO put_json/get_json monkeypatched to an in-memory store
    """
    # Override DB dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Monkeypatch MinIO helpers used by log endpoints
    from app.utils import minio_utils as minio_mod  # module with put_json/get_json

    stored_objects: dict[str, dict] = {}

    def fake_put_json(config_id: int, filename: str, data: dict) -> str:
        key = f"{config_id}/{filename}"
        # deep copy through JSON to avoid accidental shared refs
        stored_objects[key] = json.loads(json.dumps(data))
        return key

    def fake_get_json(config_id: int, filename: str) -> dict:
        key = f"{config_id}/{filename}"
        return stored_objects[key]

    monkeypatch.setattr(minio_mod, "put_json", fake_put_json)
    monkeypatch.setattr(minio_mod, "get_json", fake_get_json)

    return TestClient(app)


# --- Helper functions ---


def create_config(client: TestClient) -> int:
    """
    Create an EvaluationConfig via API and return its ID.
    Adjust the URL to your actual config-create endpoint if needed.
    """
    payload = {
        "application_name": "XR Safety Assistant",
        "ai_model_name": "xr-safety-detector-v2",
        "ai_model_type": "vision-transformer",
        "metrics": ["accuracy", "precision", "recall", "human_effort"],
        "evaluation_date": "2025-11-28T21:08:49.645Z",
        "description": "XR safety pilot test run",
        "config_type": "haic_session",
        "evaluation_status": "pending",
    }

    # Adjust if your route differs (e.g. /api/v1/configs)
    resp = client.post("/api/v1/configurations", json=payload)
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert "id" in data
    return data["id"]


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


# --- Tests ---


def test_upload_log_and_evaluate(client: TestClient):
    """
    Full walkthrough for the file-upload ingestion path:
    1. Create config
    2. Upload log file
    3. Trigger evaluation
    4. Fetch results and check basic properties
    """
    config_id = create_config(client)

    # 1) Prepare a log and send it as a "file"
    log_payload = example_log("upload-session-001")
    file_content = json.dumps(log_payload).encode("utf-8")

    # Adjust URL to your actual upload endpoint if needed
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

    # We don't assume a specific shape; just that some result-like fields exist.
    first = results[0]
    assert "id" in first or "result_minio_path" in first or "aggregates" in first


def test_register_log_and_evaluate(client: TestClient):
    """
    Full walkthrough for the JSON-register ingestion path:
    1. Create config
    2. POST /logs/register with JSON body
    3. Trigger evaluation
    4. Fetch results and verify at least one result exists
    """
    config_id = create_config(client)

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
        # Depending on your current register_log return shape
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
    assert "id" in first or "result_minio_path" in first or "aggregates" in first
