# Backend Testing Guide

This guide helps you test the refactored backend's log upload → evaluation → results flow.

## Prerequisites

1. **Database**: PostgreSQL running with the schema created via Alembic
2. **MinIO**: Object storage server running and configured
3. **Environment Variables**: Set up `.env` file with required credentials

## Quick Setup (using Docker Compose)

If you have docker-compose.yml in the root:

```bash
# Start all services
docker-compose up -d

# Run database migrations
cd backend && alembic upgrade head

# Seed core metrics (optional)
cd backend && python -c "from app.services.seed_core_metrics import seed_core_definitions; seed_core_definitions()"
```

## Testing the Flow

### 1. Start the Backend

```bash
cd backend
python main.py
```

The API will be available at: http://localhost:8000/api/docs

### 2. Create an Evaluation Configuration

**Endpoint**: `POST /api/v1/configuration/new`

**Sample Payload**:
```json
{
  "application_name": "Test App",
  "ai_model_name": "GPT-4",
  "ai_model_type": "Large Language Model",
  "description": "Testing the refactored flow",
  "metrics": ["Effectiveness", "Efficiency"],
  "config_type": "benchmark",
  "evaluation_status": "pending"
}
```

**Response**: Note the `id` returned (e.g., `1`)

### 3. Upload Logs

**Endpoint**: `POST /api/v1/logs/upload?configuration_id=1`

**Upload Method**: Form-data with `file` field containing a JSON file

**Sample Log JSON**:
```json
[
  {
    "session_id": "session_001",
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
]
```

**Expected Response**:
```json
{
  "detail": "Uploaded and processed log(s) for configuration 1.",
  "minio_paths": {
    "original": "1/uploads/log.20241205T152100.json",
    "derived_by_version": {
      "gpt-4": {
        "path": "1/uploads/log.20241205T152100.vgpt-4.derived.json",
        "summary": {...}
      }
    }
  }
}
```

### 4. Run Evaluation

**Endpoint**: `POST /api/v1/evaluate/1`

This triggers background evaluation of the uploaded logs.

**Expected Response**:
```json
{
  "detail": "Evaluation started successfully"
}
```

### 5. Check Evaluation Status

**Endpoint**: `GET /api/v1/configuration/1`

Look for `evaluation_status` in the response. It should eventually become `"completed"`.

### 6. View Results

**Endpoint**: `GET /api/v1/results/list` or check MinIO directly

Results are stored in MinIO at paths like: `1/results/{uuid}.json`

## Alternative: Register Individual Logs

Instead of uploading a file, you can register logs one by one:

**Endpoint**: `POST /api/v1/logs/register?configuration_id=1`

**Sample Payload**:
```json
{
  "session_id": "session_002",
  "user_id": "user456",
  "ai_model_version": "gpt-4",
  "app_version": "1.0.0",
  "start_time": "2024-01-01T11:00:00Z",
  "end_time": "2024-01-01T11:05:00Z",
  "interaction_data": {...}
}
```

## Validation Tests

Run the validation script to ensure core logic works:

```bash
cd backend
python test_refactored_flow.py
```

This validates:
- ✅ LogService initialization and core methods
- ✅ Data normalization logic
- ✅ Metrics core integration (external `packages/metrics_core` module)
- ✅ Sample log processing
- ✅ Error handling and edge cases

### Metrics Core Integration

The evaluation system properly integrates with the external `packages/metrics_core` library:

- **compute_from_log()** in `metrics_adapter.py` uses `metrics_core` for metric calculations
- **interaction_metrics** module for HAIC metrics (F, D, HCL, Tr, A, S, EL)
- **outcome_metrics** module for effectiveness/efficiency metrics
- All metric computations are validated in the test suite

## Troubleshooting

### Common Issues

1. **"haic_env_builder module not found"**
   - Comment out problematic routers in `main.py` for testing:
   ```python
   # api.include_router(env_builder.router, ...)
   # api.include_router(simulator.router, ...)
   ```

2. **MinIO Connection Failed**
   - Check MinIO is running: `docker ps | grep minio`
   - Verify environment variables in `backend/.env`

3. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in environment

4. **Evaluation Fails**
   - Check logs: `docker logs <container_name>`
   - Ensure configuration has `minio_path` set after upload

### Debug Commands

```bash
# Check MinIO files
docker exec -it minio mc ls local/your-bucket

# Check database
docker exec -it postgres psql -U your_user -d your_db -c "SELECT * FROM evaluation_configs;"

# View application logs
cd backend && python main.py  # Look for error messages
```
