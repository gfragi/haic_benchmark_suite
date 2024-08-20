from http import client


def test_evaluate_log():
    # Assuming a log entry and evaluation config already exist
    response = client.post("/evaluate/1")
    assert response.status_code == 200
    data = response.json()
    assert "Prediction Accuracy" in data
    assert "Response Time" in data
