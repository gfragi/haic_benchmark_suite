from app.services.evaluate import calculate_prediction_accuracy, calculate_response_time

def test_calculate_prediction_accuracy():
    interaction_data = [
        {"result": "true_positive"},
        {"result": "true_negative"},
        {"result": "false_positive"}
    ]
    accuracy = calculate_prediction_accuracy(interaction_data)
    assert accuracy == 2 / 3  # 2 correct out of 3

def test_calculate_response_time():
    interaction_data = [
        {"response_time": 1.0},
        {"response_time": 1.5},
        {"response_time": 0.5}
    ]
    avg_response_time = calculate_response_time(interaction_data)
    assert avg_response_time == 1.0  # Average of 1.0 seconds
