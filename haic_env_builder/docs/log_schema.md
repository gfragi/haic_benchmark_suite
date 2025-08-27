# Log Schema

This document defines the JSON schema for interaction logs that the Simulator and Benchmarking Suite expect.
Each decision event is one action taken by a human or AI agent during a task.

## Decision Event Schema

```json
{
  "t": 0.0,
  "agent": "RadiologistAssistant",
  "actor_type": "ai",
  "action": "classifying for task CT Scan Diagnosis",
  "latency_ms": 400.0,
  "duration_s": 0.9,
  "correct": true,
  "probs": {
    "class_A": 0.7,
    "class_B": 0.3
  },
  "surrogate_probs": {
    "class_A": 0.65,
    "class_B": 0.35
  },
  "surrogate_action": "class_A",
  "event_type": "decision"
}
````

## Field Descriptions

| Field              | Type     | Required | Description                                                          |
| ------------------ | -------- | -------- | -------------------------------------------------------------------- |
| `t`                | `float`  | ✅        | Timestamp (seconds since start of task).                             |
| `agent`            | `string` | ✅        | Name of the agent (e.g., `"RadiologistAssistant"`).                  |
| `actor_type`       | `string` | ✅        | `"human"` or `"ai"` (used for collaboration and HCL metrics).        |
| `action`           | `string` | ✅        | Action performed (free text).                                        |
| `latency_ms`       | `float`  | ❌        | Reaction latency in milliseconds.                                    |
| `duration_s`       | `float`  | ❌        | Duration of the action in seconds.                                   |
| `correct`          | `bool`   | ❌        | Whether the action was correct (for Trust and Adaptability metrics). |
| `probs`            | `object` | ❌        | Probability distribution over possible actions (for AI).             |
| `surrogate_probs`  | `object` | ❌        | Surrogate probability distribution (for Similarity metric).          |
| `surrogate_action` | `string` | ❌        | Action chosen by surrogate agent (if available).                     |
| `event_type`       | `string` | ❌        | Custom event label (e.g., `"decision"`, `"error"`, `"info"`).        |


## Full Run Artifact

When a simulation or pilot run completes, logs are wrapped in a run artifact:

```json
  {
  "sim_version": "sim-0.1.0",
  "task": {
    "name": "CT Scan Diagnosis",
    "description": "Review and diagnose CT scan results with AI assistance.",
    "parameters": {
      "image_type": "CT",
      "urgency": "high"
    }
  },
  "seed": 42,
  "config_hash": "0dfea8ce2f90",
  "started_at": "2025-08-26T12:34:56Z",
  "decisions": [ /* array of Decision Events */ ],
  "metrics": {
    "F": 0.8,
    "D": 1.2,
    "HCL": 0.33,
    "Tr": 0.9,
    "A": 0.5,
    "S": 0.7,
    "EL": 0.2
  },
  "status": "success"
}

```

| Field         | Type     | Description                                         |
| ------------- | -------- | --------------------------------------------------- |
| `sim_version` | `string` | Simulator version (e.g., `"sim-0.1.0"`).            |
| `task`        | `object` | Task definition (name, description, parameters).    |
| `seed`        | `int`    | Optional RNG seed for reproducibility.              |
| `config_hash` | `string` | Hash of input configuration (ensures traceability). |
| `started_at`  | `string` | UTC timestamp when run started (ISO-8601 with `Z`). |
| `decisions`   | `array`  | Sequence of **Decision Events**.                    |
| `metrics`     | `object` | Computed metrics (F, D, HCL, Tr, A, S, EL).         |
| `status`      | `string` | `"success"` or `"error"`.                           |


## Example Decision Logs

### Example A – Radiologist scenario

```json
{
  "t": 0.0,
  "agent": "RadiologistAssistant",
  "actor_type": "ai",
  "action": "classifying CT scan",
  "latency_ms": 400.0,
  "duration_s": 0.9,
  "correct": true
}
{
  "t": 1.5,
  "agent": "Dr. Smith",
  "actor_type": "human",
  "action": "reviewing AI suggestion",
  "latency_ms": 1200.0,
  "duration_s": 2.5,
  "correct": true
}

```

### Example B – Surrogate similarity with probs

```json
{
  "t": 5.0,
  "agent": "SurrogateAgent",
  "actor_type": "ai",
  "action": "suggest treatment",
  "probs": {"A": 0.7, "B": 0.2, "C": 0.1},
  "surrogate_probs": {"A": 0.65, "B": 0.25, "C": 0.1}
}
{
  "t": 6.0,
  "agent": "Dr. Lee",
  "actor_type": "human",
  "action": "choosing treatment",
  "probs": {"A": 0.6, "B": 0.3, "C": 0.1},
  "surrogate_probs": {"A": 0.65, "B": 0.25, "C": 0.1}
}
```


## Usage Notes

- All timestamps (t) must be relative to task start (float, seconds).

- Pilots should log one Decision Event per interaction (human or AI).

- For Trust and Adaptability, provide the correct flag whenever possible.

- For Similarity, include both probs and surrogate_probs if comparing humans to surrogate agents.

- All timestamps (t) must be relative to task start (float, seconds).

- Store logs as JSON (*.json) and submit via /logs/upload or /simulator/simulate.
