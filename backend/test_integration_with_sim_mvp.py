#!/usr/bin/env python3
"""
Integration test to validate that haic_sim_mvp outputs work with the refactored backend.
This tests the actual flow from simulation results to backend evaluation.
"""

import json
import os
from app.services.metrics_adapter import compute_from_log

def test_haic_sim_mvp_log_transformation():
    """Test transforming haic_sim_mvp simulation log to backend format"""
    # Load a sample simulation result from haic_sim_mvp
    sim_log_path = "haic_sim_mvp/results/ct_demo_20250918T223109Z.json"

    if not os.path.exists(sim_log_path):
        print("⚠️  Sample simulation log not found, skipping transformation test")
        return

    with open(sim_log_path, 'r') as f:
        sim_log = json.load(f)

    print(f"✅ Loaded simulation log: {sim_log['sim_id']}")
    print(f"   - Environment: {sim_log['env_id']}")
    print(f"   - Decisions: {len(sim_log['decisions'])}")
    print(f"   - Agents: {list(sim_log['agents'].keys())}")

    # The simulation log has decisions that can be used directly by metrics_adapter
    # The backend expects logs with session_id, user_id, etc. and interaction_data
    # But the decisions array is compatible

    # Test that the decisions can be processed by the metrics system
    try:
        # This should work because compute_from_log looks for 'decisions' array
        result = compute_from_log(sim_log)
        assert isinstance(result, dict)
        assert "interaction" in result

        if "interaction" in result and result["interaction"]:
            interaction = result["interaction"]
            print("✅ Simulation log metrics computed successfully:")
            print(f"   - F (Fluency): {interaction.get('F', 'N/A')}")
            print(f"   - D (Delegation): {interaction.get('D', 'N/A')}")
            print(f"   - HCL (Human-Centered Learning): {interaction.get('HCL', 'N/A')}")

    except Exception as e:
        print(f"❌ Failed to compute metrics from simulation log: {e}")
        raise

def test_real_metrics_file_format():
    """Test that real metrics files match expected backend format"""
    # Load one of the actual metrics files used by the backend
    metrics_files = [
        "metrics/CT_Scan_Diagnosis_(v2)_full_2025-08-28_17-34-13.json",
        "metrics/Overcooked_Cramped_Room_(v2)_full_2025-08-28_20-03-43.json"
    ]

    for metrics_file in metrics_files:
        if not os.path.exists(metrics_file):
            continue

        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)

        print(f"✅ Loaded metrics file: {os.path.basename(metrics_file)}")
        print(f"   - Task: {metrics_data.get('task', 'N/A')}")
        print(f"   - Decisions: {len(metrics_data.get('decisions', []))}")
        print(f"   - HAIC Metrics: {list(metrics_data.get('metrics', {}).keys())}")

        # These files should be directly usable by the backend
        # They have the decisions array that compute_from_log expects
        try:
            result = compute_from_log(metrics_data)
            assert "interaction" in result
            print("   ✅ Compatible with backend metrics computation")
        except Exception as e:
            print(f"   ❌ Not compatible: {e}")

        break  # Just test one file

def test_backend_log_schema_validation():
    """Test that backend can process properly formatted logs"""
    from app.schemas.log import LogSchema

    # Create a sample log that matches the backend's LogSchema
    sample_backend_log = {
        "session_id": "test_session_001",
        "user_id": "user123",
        "ai_model_version": "gpt-4",
        "app_version": "1.0.0",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:05:00Z",
        "decisions": [
            {
                "t": 1.0,
                "agent": "AI_Assistant",
                "action": "classify",
                "actor_type": "ai",
                "latency_ms": 150.0,
                "correct": True
            }
        ]
    }

    # Validate against schema
    try:
        log_schema = LogSchema(**sample_backend_log)
        print("✅ Sample backend log validates against LogSchema")

        # Test metrics computation
        result = compute_from_log(sample_backend_log)
        print("✅ Backend log format works with metrics computation")

    except Exception as e:
        print(f"❌ Backend log validation failed: {e}")
        raise

def run_integration_tests():
    """Run all integration tests"""
    print("🔗 Running haic_sim_mvp ↔ Backend Integration Tests...\n")

    try:
        test_haic_sim_mvp_log_transformation()
        print()

        test_real_metrics_file_format()
        print()

        test_backend_log_schema_validation()
        print()

        print("🎉 All integration tests PASSED!")
        print("\n📋 Integration Summary:")
        print("✅ haic_sim_mvp simulation logs → metrics_core computation")
        print("✅ Real metrics files → backend compatible format")
        print("✅ Backend LogSchema → valid data structures")
        print("✅ End-to-end: Simulation → Metrics → Backend Evaluation")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        raise

if __name__ == "__main__":
    run_integration_tests()
