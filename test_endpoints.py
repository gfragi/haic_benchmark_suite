#!/usr/bin/env python3
"""
HAIC Benchmark Suite - Endpoint Testing Script
Tests all API endpoints to ensure they are working correctly.
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, url: str, expected_status: int = 200, **kwargs) -> Dict:
    """Test a single endpoint and return results."""
    try:
        response = requests.request(method, f"{BASE_URL}{url}", **kwargs)
        success = response.status_code == expected_status

        return {
            "endpoint": url,
            "method": method,
            "status_code": response.status_code,
            "expected": expected_status,
            "success": success,
            "error": None if success else f"Expected {expected_status}, got {response.status_code}"
        }
    except Exception as e:
        return {
            "endpoint": url,
            "method": method,
            "status_code": None,
            "expected": expected_status,
            "success": False,
            "error": str(e)
        }

def main():
    print("🧪 HAIC Benchmark Suite - Endpoint Testing")
    print("=" * 50)

    # Test results
    results = []

    # 1. Health check
    print("Testing health endpoints...")
    results.append(test_endpoint("GET", "/meta/health"))

    # 2. Configuration endpoints
    print("Testing configuration endpoints...")
    results.append(test_endpoint("GET", "/api/v1/configuration"))

    # 3. Environment endpoints
    print("Testing environment endpoints...")
    results.append(test_endpoint("GET", "/api/v1/envs"))

    # 4. Survey endpoints
    print("Testing survey endpoints...")
    results.append(test_endpoint("GET", "/api/v1/survey/aggregate"))

    # 5. Simulation endpoints
    print("Testing simulation endpoints...")
    results.append(test_endpoint("GET", "/api/v1/simulator/runs_by_task?prefix=test", 422))  # 422 = validation error (expected)

    # 6. Reporting endpoints
    print("Testing reporting endpoints...")
    results.append(test_endpoint("GET", "/api/v1/reporting/time-series-data"))

    # 7. Fairness endpoints
    print("Testing fairness endpoints...")
    results.append(test_endpoint("POST", "/api/v1/fairness/evaluate/", 422))  # 422 = validation error (expected without data)

    # 8. API documentation
    print("Testing API documentation...")
    results.append(test_endpoint("GET", "/api/docs"))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    successful = 0
    failed = 0

    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['method']} {result['endpoint']}")
        if result["error"]:
            print(f"   Error: {result['error']}")

        if result["success"]:
            successful += 1
        else:
            failed += 1

    print("\n" + "=" * 50)
    print(f"🎯 OVERALL RESULTS: {successful} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! The HAIC Benchmark Suite is fully operational.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
