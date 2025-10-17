# HAIC Benchmark Suite — Public API (v1)

**Base URL (local dev):** `http://localhost:8000/api/v1`

All endpoints return JSON. Errors use a standard envelope:

```json
{
    "error": {
        "code": "NOT_FOUND",
        "message": "Config not found",
        "details": { "name": "CT_Scan_Diagnosis_env.yaml" }
    }
}
```

---

## Meta

### `GET /health`

Liveness probe.

**Response:**  
`200 OK`
```json
{ "status": "ok", "uptime_s": 12.34 }
```

### `GET /version`

Service metadata.

**Response:**  
`200 OK`
```json
{
    "service": "haic-benchmark-suite",
    "version": "0.3.0-dev",
    "commit": "local"
}
```

---

## Environment Builder

### `POST /env/generate_config`

Create and persist a YAML config under `haic_env_builder/configs/`.

**Body:**
```json
{
    "task_name": "CT Scan Diagnosis",
    "task_parameters": { "image_type": "CT", "urgency": "high", "report_required": true },
    "agent_definitions": [
        { "name": "RadiologistAssistant", "capabilities": ["classify","highlight","summarize"], "modality": "text" },
        { "name": "VoiceSupportBot", "capabilities": ["speak","respond"], "modality": "audio" }
    ],
    "profile_definitions": [
        { "id": "user123", "skill_level": "expert", "role": "radiologist" },
        { "id": "user456", "skill_level": "novice", "role": "technician" }
    ]
}
```

**Responses:**

- `201/200 OK`
    ```json
    { "message": "Environment config generated", "path": "haic_env_builder/configs/CT_Scan_Diagnosis_env.yaml" }
    ```
- `422 Unprocessable Entity`
    ```json
    {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid agent schema",
            "details": { "index": 1, "field": "capabilities" }
        }
    }
    ```

---

### `GET /env/list_configs`

List available YAML configs.

**Response:**  
`200 OK`
```json
{ "available_configs": ["CT_Scan_Diagnosis_env.yaml","Kitchen_Toy_env.yaml"] }
```

---

### `GET /env/load_config?name=<file.yaml>`

Fetch a stored YAML config.

**Response:**  
`200 OK`
```json
{
    "config": {
        "task": {
            "name": "CT Scan Diagnosis",
            "description": "Auto-generated task",
            "parameters": { "image_type": "CT", "urgency": "high", "report_required": true }
        },
        "agents": [
            { "name":"RadiologistAssistant","capabilities":["classify","highlight","summarize"],"modality":"text" },
            { "name":"VoiceSupportBot","capabilities":["speak","respond"],"modality":"audio" }
        ],
        "profiles": [
            { "id":"user123","skill_level":"expert","role":"radiologist" },
            { "id":"user456","skill_level":"novice","role":"technician" }
        ]
    }
}
```

- `404 Not Found`
    ```json
    { "error": { "code": "NOT_FOUND", "message": "Config not found", "details": { "name": "foo.yaml" } } }
    ```

---

## Simulator

### `POST /simulator/simulate?name=<file.yaml>&seed=<int?>`

Runs a simulation using the given config. Optional seed for reproducibility.

**Response:**  
`200 OK`
```json
{
    "simulation_result": {
        "task": {
            "name": "CT Scan Diagnosis",
            "description": "Auto-generated task",
            "parameters": { "image_type": "CT", "urgency": "high", "report_required": true }
        },
        "agents": ["RadiologistAssistant","VoiceSupportBot"],
        "profiles": ["user123","user456"],
        "metrics": { "F": 0.75, "D": 0.85, "HCL": 0.20, "Tr": 1.00, "A": 0.20, "S": 0.95, "EL": 0.41 },
        "decisions": [
            { "step": 0, "agent": "RadiologistAssistant", "action": "classifying for task CT Scan Diagnosis" },
            { "step": 0, "agent": "VoiceSupportBot", "action": "performing speak" }
            // ...
        ],
        "status": "success",
        "seed": 42,
        "config_hash": "0dfea8ce2f90",
        "log_path": "metrics/CT_Scan_Diagnosis_metrics_20250724_180410.json"
    }
}
```

- `404 Not Found`
    ```json
    { "error": { "code": "NOT_FOUND", "message": "Configuration not found", "details": { "name": "x.yaml" } } }
    ```

---

## Metrics

### `GET /metrics/list`

List all metrics JSON artifacts under `metrics/`.

**Response:**  
`200 OK`
```json
{ "files": ["CT_Scan_Diagnosis_metrics_20250724_180410.json","Kitchen_Toy_Task_metrics_20250825_235411.json"] }
```

---

### `GET /metrics/list_by_task?prefix=<task name or prefix>`

Filter metrics files by task prefix (case-insensitive; spaces ignored by `_`).

**Response:**  
`200 OK`
```json
{ "files": ["CT_Scan_Diagnosis_metrics_20250724_180410.json"] }
```

---

### `GET /metrics/load?file=<metrics.json>`

Load one metrics artifact (full simulation envelope or metrics-only, depending on writer).

**Response:**  
`200 OK`
```json
{
    "metrics": {
        "task": "CT Scan Diagnosis",
        "seed": 42,
        "config_hash": "0dfea8ce2f90",
        "metrics": { "F": 0.75, "D": 0.85, "HCL": 0.20, "Tr": 1.00, "A": 0.20, "S": 0.95, "EL": 0.41 },
        "decisions": [ /* ... */ ]
    }
}
```

- `404 Not Found`
    ```json
    { "error": { "code": "NOT_FOUND", "message": "Metrics file not found", "details": { "file": "x.json" } } }
    ```
- `500 I/O Error`
    ```json
    { "error": { "code": "IO_ERROR", "message": "Failed to read metrics", "details": { "file": "x.json", "error": "..." } } }
    ```

---

## Curl Quickstart

```sh
# Health & version
curl -s http://localhost:8000/api/v1/health
curl -s http://localhost:8000/api/v1/version

# List & load configs
curl -s http://localhost:8000/api/v1/env/list_configs
curl -s "http://localhost:8000/api/v1/env/load_config?name=CT_Scan_Diagnosis_env.yaml"

# Simulate
curl -s -X POST "http://localhost:8000/api/v1/simulator/simulate?name=CT_Scan_Diagnosis_env.yaml&seed=42"

# Browse metrics
curl -s http://localhost:8000/api/v1/metrics/list
curl -s "http://localhost:8000/api/v1/metrics/list_by_task?prefix=CT Scan"
curl -s "http://localhost:8000/api/v1/metrics/load?file=CT_Scan_Diagnosis_metrics_20250724_180410.json"
```

---

## Status Codes

- **200 OK** — Successful read or compute.
- **201 Created** — (If you choose to use for generate_config.)
- **400 Bad Request** — Malformed query/body.
- **404 Not Found** — Missing config/metrics file.
- **422 Unprocessable Entity** — Schema/validation error.
- **500 Internal Server Error** — Unexpected exceptions or I/O failures.

---

## Notes & Guarantees

- **Versioning:** All endpoints live under `/api/v1/*`. Breaking changes will bump the version prefix.
- **Reproducibility:** Where supported, `seed` enforces deterministic behavior of the simulator logic that depends on RNG.
- **Artifacts:** Simulator writes metrics to `metrics/<task>_metrics_<timestamp>.json`. Consumers should treat these as immutable run artifacts.
- **Schemas:** Internally, FastAPI Pydantic models validate responses:  
    `MessageWithPath`, `ConfigList`, `SimulationEnvelope`, `MetricsList`, `MetricsEnvelope`, `ErrorEnvelope`.
- **OpenAPI/Swagger:**  
    - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
    - OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)