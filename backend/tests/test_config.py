from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_configuration():
    response = client.post("/evaluation/config", json={
        "application_name": "RadiologyApp",
        "ai_model_name": "TumorDetectionModelV1",
        "metrics": [
            {"metric_name": "Prediction Accuracy", "metric_formula": "TP + TN / Total Predictions", "description": "Accuracy of predictions"},
            {"metric_name": "Response Time", "metric_formula": "Total Response Time / Number of Queries", "description": "Average time per query"}
        ],
        "evaluation_date": "2024-07-01",
        "description": "Evaluation of Tumor Detection Model in RadiologyApp"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["application_name"] == "RadiologyApp"
    assert len(data["metrics"]) == 2

def test_get_configuration():
    response = client.get("/evaluation/config/1")
    assert response.status_code == 200
    data = response.json()
    assert data["configuration_id"] == 1
    assert data["application_name"] == "RadiologyApp"
