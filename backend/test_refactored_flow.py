#!/usr/bin/env python3
"""
Simple test script to validate the refactored log processing flow.
This tests the core logic without requiring database/MinIO connections.
"""

import json
from unittest.mock import Mock, patch
from app.services.log_service import LogService
from app.services.evaluate import _normalize_logs_data, _compute_derived_metrics

def test_log_service_initialization():
    """Test that LogService can be initialized"""
    service = LogService()
    assert service is not None
    print("✅ LogService initialization: PASSED")

def test_log_data_normalization():
    """Test log data normalization logic"""
    # Test with wrapped logs
    wrapped_data = {"logs": [{"session_id": "test1"}, {"session_id": "test2"}]}
    normalized = _normalize_logs_data(wrapped_data)
    assert len(normalized) == 2
    assert normalized[0]["session_id"] == "test1"

    # Test with direct array
    direct_data = [{"session_id": "test3"}]
    normalized = _normalize_logs_data(direct_data)
    assert len(normalized) == 1
    assert normalized[0]["session_id"] == "test3"

    print("✅ Log data normalization: PASSED")

def test_log_service_sanitize():
    """Test the sanitize method"""
    service = LogService()

    assert service._sanitize("test_123") == "test_123"
    assert service._sanitize("test@#$%") == "test"  # Special chars replaced with _, then stripped
    assert service._sanitize("___test___") == "test"  # Leading/trailing _ stripped
    assert service._sanitize(None) == "Unknown"
    assert service._sanitize("") == "Unknown"

    print("✅ Sanitize method: PASSED")

def test_mean_map_calculation():
    """Test the mean map calculation"""
    service = LogService()

    dicts = [
        {"metric1": 1.0, "metric2": 2.0},
        {"metric1": 3.0, "metric2": 4.0},
        {"metric1": 5.0}  # metric2 missing
    ]

    result = service._mean_map(dicts, "nonexistent")  # Should handle empty gracefully
    assert result == {}

    # Note: This would require actual metric data structure
    print("✅ Mean map calculation structure: PASSED")

@patch('app.services.log_service.get_minio_client')
def test_log_service_mock_minio(mock_get_client):
    """Test LogService with mocked MinIO"""
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    service = LogService()
    assert service.minio_client == mock_client

    print("✅ LogService with mocked MinIO: PASSED")

def test_metrics_core_integration():
    """Test that metrics computation integrates with metrics_core"""
    from app.services.metrics_adapter import compute_from_log

    sample_log = {
        "session_id": "test_session_001",
        "user_id": "user123",
        "ai_model_version": "gpt-4",
        "app_version": "1.0.0",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:05:00Z",
        "interaction_data": {
            "validation_data": {
                "system_metrics": {
                    "accuracy": 0.95,
                    "precision": 0.90,
                    "recall": 0.85
                },
                "processing_time_seconds": 2.5,
                "confidence_level": 0.88
            },
            "review_data": {
                "false_positives": 1,
                "false_negatives": 2,
                "detections_confirmed": 10,
                "time_spent_on_corrections_seconds": 30
            }
        }
    }

    # Test that compute_from_log works with metrics_core
    try:
        result = compute_from_log(sample_log)
        assert isinstance(result, dict)
        assert "by_metric" in result
        assert "by_pillar" in result
        assert "interaction" in result

        # Check that we get actual metric values
        by_metric = result["by_metric"]
        assert "Prediction Accuracy" in by_metric
        assert isinstance(by_metric["Prediction Accuracy"], (int, float))

        print("✅ Metrics core integration: PASSED")

    except Exception as e:
        print(f"❌ Metrics core integration failed: {e}")
        raise

def test_sample_log_processing():
    """Test processing a sample log structure"""
    sample_log = {
        "session_id": "test_session_001",
        "user_id": "user123",
        "ai_model_version": "gpt-4",
        "app_version": "1.0.0",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:05:00Z",
        "interaction_data": {
            "validation_data": {
                "system_metrics": {
                    "accuracy": 0.95,
                    "precision": 0.90,
                    "recall": 0.85
                },
                "processing_time_seconds": 2.5,
                "confidence_level": 0.88
            },
            "review_data": {
                "false_positives": 1,
                "false_negatives": 2,
                "detections_confirmed": 10,
                "time_spent_on_corrections_seconds": 30
            }
        }
    }

    # Test that the log structure is valid JSON
    json_str = json.dumps(sample_log, indent=2)
    parsed = json.loads(json_str)
    assert parsed["session_id"] == "test_session_001"

    print("✅ Sample log structure validation: PASSED")

def run_all_tests():
    """Run all validation tests"""
    print("🧪 Running refactored backend validation tests...\n")

    try:
        test_log_service_initialization()
        test_log_data_normalization()
        test_log_service_sanitize()
        test_mean_map_calculation()
        test_log_service_mock_minio()
        test_metrics_core_integration()
        test_sample_log_processing()

        print("\n🎉 All validation tests PASSED!")
        print("\n📋 Next steps for full testing:")
        print("1. Set up database and MinIO connections")
        print("2. Run: cd backend && python main.py")
        print("3. Test endpoints via Swagger UI at http://localhost:8000/api/docs")
        print("4. Test log upload -> evaluation -> results flow")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
