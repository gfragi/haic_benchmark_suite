from http import client


def test_create_log():
    response = client.post("/logs/", json={
        "session_id": "unique_session_id",
        "user_id": "unique_user_id",
        "ai_model_version": "1.0.0",
        "app_version": "1.0.0",
        "start_time": "2024-06-28T12:00:00Z",
        "end_time": "2024-06-28T12:30:00Z",
        "configuration_id": 1,
        "interaction_data": [],
        "retrain_events": []
    })
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "unique_session_id"
    assert data["configuration_id"] == 1
