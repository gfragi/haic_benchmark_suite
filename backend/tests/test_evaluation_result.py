from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_evaluation_result():
    response = client.post("/results", json={
        "log_id": 1,
        "metrics": {
            "Prediction Accuracy": 0.95,
            "Response Time": 0.5
        },
        "evaluation_date": "2024-07-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["log_id"] == 1
    assert data["metrics"]["Prediction Accuracy"] == 0.95

def test_get_evaluation_result():
    response = client.get("/results/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "metrics" in data
