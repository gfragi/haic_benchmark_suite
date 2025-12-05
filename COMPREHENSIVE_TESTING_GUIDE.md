# HAIC Benchmark Suite - Comprehensive Testing Guide

## Overview
This guide provides complete testing workflows for the HAIC Benchmark Suite, covering all features from backend API testing to frontend integration verification.

## 🚀 Quick Start Testing

### 1. Backend Health Check
```bash
# Start all services
make dev

# Verify services are healthy
make health

# Should show:
# Backend: UP
# MinIO: UP
# Database: Connected
```

### 2. API Documentation Access
```bash
# Interactive API docs
open http://localhost:8000/api/docs

# OpenAPI schema
open http://localhost:8000/api/openapi.json
```

## 📋 Complete Feature Testing Workflows

### Workflow 1: Configuration & Evaluation Pipeline

#### Step 1: Create Evaluation Configuration
```bash
# Create a new evaluation configuration
curl -X POST "http://localhost:8000/api/v1/configuration/new" \
  -H "Content-Type: application/json" \
  -d '{
    "application_name": "Test App",
    "ai_model_name": "TestModel",
    "ai_model_type": "Classification",
    "description": "Test evaluation configuration",
    "metrics": ["accuracy", "efficiency", "fairness"],
    "config_type": "comprehensive"
  }'
```

#### Step 2: List Configurations
```bash
# Get all configurations
curl "http://localhost:8000/api/v1/configuration" | jq .
```

#### Step 3: Upload Test Logs
```bash
# Upload sample interaction logs (replace with actual log file)
curl -X POST "http://localhost:8000/api/v1/logs/upload?configuration_id=1" \
  -F "file=@sample_logs.json" \
  -F "filename=sample_logs.json"
```

#### Step 4: Trigger Evaluation
```bash
# Start evaluation for configuration ID 1
curl -X POST "http://localhost:8000/api/v1/evaluate/1"
```

#### Step 5: Check Results
```bash
# Get evaluation results
curl "http://localhost:8000/api/v1/results/1" | jq .
```

### Workflow 2: Environment & Simulation Testing

#### Step 1: Browse Available Environments
```bash
# List all pre-built environments
curl "http://localhost:8000/api/v1/envs" | jq .

# Should return environments like:
# - CT_Diagnosis (Medical)
# - SE_ENV (Energy)
# - MFG_ENV (Manufacturing)
# - ST_AL_ENV (Customer Support)
# - NS_ENV (Healthcare)
```

#### Step 2: Get Environment Details
```bash
# Get specific environment info
curl "http://localhost:8000/api/v1/envs/CT_Diagnosis" | jq .
```

#### Step 3: Run Simulation
```bash
# List available simulation runs
curl "http://localhost:8000/api/v1/simulator/runs_by_task?prefix=CT_Diagnosis" | jq .
```

#### Step 4: Generate Custom Environment
```bash
# Generate custom environment configuration
curl -X POST "http://localhost:8000/api/v1/env/generate_config" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "medical",
    "task": "diagnosis",
    "agents": ["radiologist", "ai_assistant"],
    "custom_requirements": {}
  }'
```

### Workflow 3: Fairness Analysis Testing

#### Step 1: Prepare Fairness Test Data
```bash
# Create test data for fairness evaluation
curl -X POST "http://localhost:8000/api/v1/fairness/evaluate/" \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [1, 0, 1, 1, 0],
    "labels": [1, 0, 0, 1, 1],
    "sensitive_features": {
      "gender": ["M", "F", "M", "F", "M"],
      "age_group": ["young", "old", "young", "old", "young"]
    }
  }'
```

#### Step 2: Test Fairness by Gender
```bash
# Note: This endpoint expects the sensitive feature as a query parameter
# The implementation may need adjustment for proper testing
```

### Workflow 4: Survey System Testing

#### Step 1: Submit Survey Response
```bash
# Submit a SUS survey response
curl -X POST "http://localhost:8000/api/v1/survey" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "pilot_tag": "CT_Diagnosis",
    "app_version": "1.0.0",
    "ai_model_version": "2.1.0",
    "tam_sus_responses": {
      "q1": 5, "q2": 4, "q3": 5, "q4": 3, "q5": 5,
      "q6": 4, "q7": 5, "q8": 4, "q9": 3, "q10": 5
    },
    "ethics_responses": {
      "trustworthy": 4,
      "fair": 4,
      "usable": 5
    }
  }'
```

#### Step 2: Get Survey Aggregates
```bash
# Get aggregated survey metrics
curl "http://localhost:8000/api/v1/survey/aggregate" | jq .

# Get metrics for specific pilot
curl "http://localhost:8000/api/v1/survey/aggregate?pilot_tag=CT_Diagnosis" | jq .
```

#### Step 3: Compare Versions
```bash
# Compare survey results between versions
curl "http://localhost:8000/api/v1/survey/compare?pilot_tag=CT_Diagnosis&version_a=1.0.0&version_b=2.0.0" | jq .
```

### Workflow 5: Reporting & Analytics

#### Step 1: Generate Time Series Data
```bash
# Get time series analytics
curl "http://localhost:8000/api/v1/reporting/time-series-data" | jq .
```

#### Step 2: Aggregate by Date
```bash
# Get date-based aggregations
curl "http://localhost:8000/api/v1/reporting/aggregate-by-date" | jq .
```

#### Step 3: Generate Comprehensive Report
```bash
# Generate evaluation report
curl -X POST "http://localhost:8000/api/v1/reporting/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "configuration_ids": [1, 2],
    "include_fairness": true,
    "include_surveys": true,
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-12-31"
    }
  }'
```

### Workflow 6: Collaboration Metrics

#### Step 1: Compute Collaboration Metrics
```bash
# Compute metrics from interaction logs
curl -X POST "http://localhost:8000/api/v1/collab-metrics/collab/compute" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      {
        "agent": "human",
        "action": "review",
        "timestamp": "2025-01-01T10:00:00Z"
      },
      {
        "agent": "ai",
        "action": "suggest",
        "timestamp": "2025-01-01T10:01:00Z"
      }
    ]
  }'
```

#### Step 2: Get Metrics from Run
```bash
# Get collaboration metrics for specific run
curl "http://localhost:8000/api/v1/collab-metrics/collab/from-run/123" | jq .
```

## 🔍 Frontend-Backend Integration Testing

### 1. Frontend Service Check
```bash
# Check if frontend is running
curl -s "http://localhost:8080" | head -10

# Should return HTML content from Vue.js app
```

### 2. CORS Testing
```bash
# Test CORS headers from frontend origin
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "http://localhost:8000/api/v1/configuration" \
     -v
```

### 3. End-to-End Workflow Testing

#### Complete Evaluation Flow:
1. **Frontend**: User selects environment from catalog
   ```javascript
   // Frontend calls
   fetch('/api/v1/envs')
     .then(r => r.json())
     .then(envs => console.log('Available environments:', envs));
   ```

2. **Frontend**: User creates configuration
   ```javascript
   // Frontend creates config
   fetch('/api/v1/configuration/new', {
     method: 'POST',
     body: JSON.stringify(configData)
   });
   ```

3. **Frontend**: User uploads logs
   ```javascript
   // Frontend uploads logs
   const formData = new FormData();
   formData.append('file', logFile);
   fetch('/api/v1/logs/upload?configuration_id=1', {
     method: 'POST',
     body: formData
   });
   ```

4. **Frontend**: User triggers evaluation
   ```javascript
   // Frontend starts evaluation
   fetch('/api/v1/evaluate/1', { method: 'POST' })
     .then(r => r.json())
     .then(result => console.log('Evaluation started:', result));
   ```

5. **Frontend**: User views results
   ```javascript
   // Frontend displays results
   fetch('/api/v1/results/1')
     .then(r => r.json())
     .then(results => {
       // Display HAIC metrics, fairness analysis, etc.
       console.log('Evaluation results:', results);
     });
   ```

## 🧪 Automated Testing Scripts

### Create Test Script
```bash
#!/bin/bash
# comprehensive_test.sh

echo "🧪 Starting HAIC Benchmark Suite Comprehensive Testing"

# 1. Health checks
echo "📊 Checking service health..."
make health

# 2. API endpoint tests
echo "🔗 Testing API endpoints..."

# Test configurations
echo "Testing configurations..."
curl -s "http://localhost:8000/api/v1/configuration" > /dev/null && echo "✅ Configurations OK" || echo "❌ Configurations FAILED"

# Test environments
echo "Testing environments..."
curl -s "http://localhost:8000/api/v1/envs" > /dev/null && echo "✅ Environments OK" || echo "❌ Environments FAILED"

# Test surveys
echo "Testing surveys..."
curl -s "http://localhost:8000/api/v1/survey/aggregate" > /dev/null && echo "✅ Surveys OK" || echo "❌ Surveys FAILED"

echo "🎉 Testing complete!"
```

### Run Automated Tests
```bash
chmod +x comprehensive_test.sh
./comprehensive_test.sh
```

## 📊 Performance Testing

### Load Testing
```bash
# Test concurrent evaluation requests
for i in {1..10}; do
  curl -s "http://localhost:8000/api/v1/evaluate/1" &
done
wait
echo "Load test complete"
```

### Memory Usage Check
```bash
# Check backend memory usage
docker stats haic-backend --no-stream

# Check database connections
docker exec haic-postgres psql -U haic_user -d haic_benchmark -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'haic_benchmark';"
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Backend Not Starting
```bash
# Check logs
make logs-backend

# Restart services
make clean
make dev
```

#### Database Connection Issues
```bash
# Check database health
docker exec haic-postgres pg_isready -U haic_user -d haic_benchmark

# Reset database
make clean
make dev
```

#### CORS Issues
```bash
# Verify CORS headers
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "http://localhost:8000/api/v1/configuration" \
     -I
```

#### File Upload Issues
```bash
# Check MinIO connectivity
curl -s "http://localhost:9000/minio/health/live"

# Verify bucket exists
docker exec haic-minio mc ls local/benchmarking-suite/
```

## 📈 Monitoring & Observability

### Health Endpoints
```bash
# Backend health
curl "http://localhost:8000/meta/health"

# System metrics (if implemented)
curl "http://localhost:8000/meta/metrics"
```

### Log Monitoring
```bash
# View all service logs
make logs

# Monitor specific service
make logs-backend

# Follow logs in real-time
docker-compose logs -f backend
```

## 🎯 Success Criteria

### ✅ All Tests Pass When:
- [ ] All services show healthy status (`make health`)
- [ ] All API endpoints return valid responses
- [ ] Frontend loads successfully on port 8080
- [ ] CORS headers allow frontend-backend communication
- [ ] Complete evaluation workflow works end-to-end
- [ ] Survey submission and aggregation functions
- [ ] Fairness analysis produces valid metrics
- [ ] Environment catalog loads all scenarios
- [ ] File uploads work with MinIO storage
- [ ] Database operations complete without errors

### 📊 Performance Benchmarks:
- [ ] API response time < 500ms for simple queries
- [ ] Evaluation completion < 30 seconds for test data
- [ ] Concurrent requests handled without errors
- [ ] Memory usage remains stable under load

---

**This comprehensive testing guide ensures the HAIC Benchmark Suite operates correctly across all features and integrations.**
