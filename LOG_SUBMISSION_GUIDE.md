# HAIC Benchmark Suite - Log Submission and Evaluation Guide

## Overview

The HAIC Benchmark Suite provides two primary methods for submitting logs for evaluation: **Upload** and **Register**. Both methods allow you to submit interaction logs from your Human-AI collaboration sessions, but they differ in their approach and use cases.

## Two Submission Methods

### 1. Log Upload (`POST /api/v1/logs/upload`)
**Best for**: Bulk submissions, large datasets, or when you want the system to handle log processing automatically.

#### When to Use:
- Submitting multiple log files at once
- When logs are stored as separate JSON files
- When you want automatic parsing and processing
- For batch processing workflows

#### Flow:
```
1. Prepare Configuration → 2. Upload Logs → 3. Automatic Processing → 4. View Results
```

#### API Usage:
```bash
# First, create a configuration
curl -X POST "http://localhost:8000/api/v1/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "application_name": "Your App Name",
    "ai_model_name": "Your AI Model",
    "ai_model_type": "vision-transformer",
    "metrics": ["accuracy", "precision", "recall"],
    "description": "Your test description",
    "config_type": "haic_session",
    "evaluation_status": "pending"
  }'

# Then upload log files
curl -X POST "http://localhost:8000/api/v1/logs/upload?configuration_id=1" \
  -F "file=@your_log_file.json"
```

#### Data Format:
- Single JSON file with log data
- Or array of log objects in one file
- Automatic parsing and metric computation

---

### 2. Log Register (`POST /api/v1/logs/register`)
**Best for**: Real-time submissions, individual sessions, or when you want full control over data processing.

#### When to Use:
- Submitting logs one session at a time
- Real-time logging during active sessions
- When you want immediate feedback on derived metrics
- For integration with live applications
- When you need to customize metric computation

#### Flow:
```
1. Prepare Configuration → 2. Register Individual Logs → 3. Immediate Metric Computation → 4. View Results
```

#### API Usage:
```bash
# First, create a configuration
curl -X POST "http://localhost:8000/api/v1/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "application_name": "Your App Name",
    "ai_model_name": "Your AI Model",
    "ai_model_type": "vision-transformer",
    "metrics": ["accuracy", "precision", "recall"],
    "description": "Your test description",
    "config_type": "haic_session",
    "evaluation_status": "pending"
  }'

# Then register individual log sessions
curl -X POST "http://localhost:8000/api/v1/logs/register?configuration_id=1" \
  -H "Content-Type: application/json" \
  -d @your_log_data.json
```

#### Data Format:
- Individual log session as JSON object
- Immediate computation of derived metrics
- Detailed response with computed metrics

## Complete Workflow

### Step 1: Create Configuration
Before submitting any logs, you must create an evaluation configuration that defines:
- Application and AI model details
- Metrics to evaluate
- Evaluation parameters

**Required Fields:**
- `application_name`: Name of your application
- `ai_model_name`: Name/version of your AI model
- `ai_model_type`: Type of AI model (e.g., "vision-transformer")
- `metrics`: Array of metric names to evaluate
- `description`: Description of the evaluation
- `config_type`: Usually "haic_session"
- `evaluation_status`: Usually "pending"

### Step 2: Submit Logs

#### Option A: Upload Method
```bash
# Upload multiple logs in one file
curl -X POST "http://localhost:8000/api/v1/logs/upload?configuration_id=1" \
  -F "file=@batch_logs.json"
```

**Response:**
```json
{
  "detail": "Uploaded and processed log(s) for configuration 1.",
  "minio_paths": {
    "original": "1/uploads/batch_logs.20251208T120000.json",
    "derived_by_version": {
      "2.0.1": {
        "path": "1/uploads/batch_logs.20251208T120000.v2.0.1.derived.json",
        "summary": {...}
      }
    }
  }
}
```

#### Option B: Register Method
```bash
# Register individual session logs
curl -X POST "http://localhost:8000/api/v1/logs/register?configuration_id=1" \
  -H "Content-Type: application/json" \
  -d @single_session_log.json
```

**Response:**
```json
{
  "detail": "Registered log.",
  "configuration_id": 1,
  "log_id": 1,
  "minio_paths": {
    "derived": "1/uploads/session-001.20251208T120000.derived.json"
  },
  "derived": {
    "by_metric": {
      "Prediction Accuracy": 0.85,
      "Precision": 0.88,
      "Recall": 0.82,
      ...
    },
    "by_pillar": {
      "Effectiveness": 0.85,
      "Efficiency": 0.92,
      ...
    },
    "interaction": {
      "F": 0.0,
      "D": 2.3,
      "HCL": 0.54,
      ...
    }
  }
}
```

### Step 3: Evaluation Process
After logs are submitted, the system automatically:

1. **Stores raw logs** in MinIO object storage
2. **Computes derived metrics** using the HAIC evaluation framework
3. **Aggregates results** across all logs in the configuration
4. **Generates evaluation reports** with pillar scores and detailed metrics

### Step 4: View Results

#### Check Configuration Status
```bash
# Get configuration details
curl -X GET "http://localhost:8000/api/v1/configurations/1"
```

#### View Evaluation Results
```bash
# Get results for a configuration
curl -X GET "http://localhost:8000/api/v1/results?configuration_id=1"
```

#### Access Stored Logs
```bash
# List all logs for a configuration
curl -X GET "http://localhost:8000/api/v1/logs/1"

# Download specific log file
curl -X GET "http://localhost:8000/api/v1/logs/download/1/log_filename.json"
```

## Data Format Requirements

### Log Session Structure
Each log session must contain:

```json
{
  "session_id": "unique_session_identifier",
  "user_id": "user_identifier",
  "ai_model_version": "1.0.0",
  "app_version": "2.0.0",
  "start_time": "2025-11-28T22:30:35.000Z",
  "end_time": "2025-11-28T22:35:35.000Z",
  "interaction_data": {
    "image_id": "img-123",
    "presentation_time": "2025-11-28T22:30:40.000Z",
    "validation_data": {
      "ai_detection_results": "OK",
      "confidence_scores": {"class_A": 0.85},
      "validation_results": "OK",
      "confidence_level": 0.75,
      "processing_time_seconds": 5.0,
      "validation_time": "2025-11-28T22:30:45.000Z",
      "system_metrics": {
        "accuracy": 0.8,
        "precision": 0.86,
        "recall": 0.78
      }
    },
    "review_data": {
      "review_time_seconds": 9,
      "detections_confirmed": 9,
      "false_positives": 1,
      "false_negatives": 0,
      "time_spent_on_corrections_seconds": 4,
      "human_confirmation_rate": 0.78
    }
  },
  "performance_logs": {
    "processing_time_seconds": {"pipeline": 5.0},
    "resource_utilization": {"cpu": 0.65, "memory": 0.8},
    "human_effort_seconds": {"annotator": 38}
  },
  "ai_model_data": {
    "ai_model_name": "your-model-v2",
    "training_data": "internal",
    "ai_model_size": "1B",
    "inference_time_seconds": 0.22,
    "deployment_details": "docker"
  },
  "decisions": [
    {
      "t": 0,
      "agent": "annotator",
      "actor_type": "human",
      "action": "inspect",
      "duration_s": 2.3,
      "correct": true
    }
  ]
}
```

### Required Fields:
- `session_id`: Unique identifier for the session
- `user_id`: User identifier
- `start_time`, `end_time`: ISO 8601 timestamps
- `app_version`, `ai_model_version`: Version strings

### Metric Computation
The system computes metrics in three categories:

1. **By Metric**: Individual metric scores (accuracy, precision, etc.)
2. **By Pillar**: Aggregated scores for HAIC pillars (Effectiveness, Efficiency, etc.)
3. **Interaction Metrics**: Detailed interaction-level metrics (F, D, HCL, etc.)

## Best Practices

### Choosing Upload vs Register
- **Use Upload** for: Batch processing, large datasets, automated workflows
- **Use Register** for: Real-time logging, individual sessions, immediate feedback

### Data Quality
- Ensure all timestamps are valid ISO 8601 format
- Include as much interaction data as possible for comprehensive evaluation
- Use consistent metric names across sessions
- Validate JSON structure before submission

### Error Handling
- Check HTTP status codes (200 = success, 4xx = client error, 5xx = server error)
- Review error messages for validation issues
- Ensure configuration exists before submitting logs
- Verify MinIO paths in responses for data storage confirmation

### Performance Considerations
- Register method provides immediate feedback but processes one session at a time
- Upload method handles bulk data but requires waiting for batch processing
- Large files (>10MB) should be split into multiple upload requests

## Support and Troubleshooting

### Common Issues
1. **"Configuration not found"**: Ensure you create a configuration first
2. **"Invalid JSON file"**: Validate JSON structure and required fields
3. **Schema validation errors**: Check data types (floats allowed for CPU/memory metrics)

### Getting Help
- Check API documentation at `http://localhost:8000/api/docs`
- Review response error messages for specific validation issues
- Ensure all required fields are present in your log data

## Next Steps

After submitting logs and receiving evaluation results:
1. Analyze the computed metrics and pillar scores
2. Compare results across different AI model versions
3. Identify areas for improvement in your Human-AI collaboration
4. Iterate on your system design based on evaluation insights

The HAIC framework provides comprehensive metrics to help you optimize the collaboration between humans and AI systems for better performance and user experience.
