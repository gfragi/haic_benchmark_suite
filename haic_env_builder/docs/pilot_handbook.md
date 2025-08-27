# Pilot Handbook

This handbook describes how pilots should log interactions and how the Benchmark Suite computes Human–AI Collaboration (HAIC) metrics.
It ensures data collection is consistent across pilots and metrics are reproducible.

## 1. Log Schema

Each decision (interaction event) must be logged in JSON with the following fields:

| Field            | Type   | Required | Description                                                              |
|------------------|--------|----------|--------------------------------------------------------------------------|
| `t`              | float  | ✔        | Timestamp (seconds since start of task).                                 |
| `agent`          | string | ✔        | Name/ID of the acting agent (human or AI).                               |
| `actor_type`     | string | ✔        | `"human"` or `"ai"`.                                                     |
| `action`         | string | ✔        | Description of the action performed.                                     |
| `latency_ms`     | float  | ✖        | Reaction time in milliseconds (if available).                            |
| `duration_s`     | float  | ✖        | Duration of the action in seconds (alternative to latency).              |
| `correct`        | bool   | ✖        | Whether the action was correct (`true`/`false`).                         |
| `event_type`     | string | ✖        | `"error"`, `"override"`, `"success"`, etc.                               |
| `probs`          | dict   | ✖        | Probability distribution over actions for human decisions (optional).     |
| `surrogate_probs`| dict   | ✖        | Probability distribution over actions for surrogate agent (optional).     |
| `surrogate_action`| string| ✖        | Action taken by surrogate for comparison.                                |

**Example Log (`decisions.json`):**

```json
{
    "decisions": [
        {
            "t": 0.0,
            "agent": "RadiologistAssistant",
            "actor_type": "ai",
            "action": "classify CT scan",
            "latency_ms": 400,
            "duration_s": 0.9,
            "correct": true
        },
        {
            "t": 1.2,
            "agent": "Dr. Smith",
            "actor_type": "human",
            "action": "confirm diagnosis",
            "latency_ms": 800,
            "duration_s": 1.1,
            "correct": true
        }
    ]
}
```

## 2. Computed Metrics

The system computes seven metrics grouped into framework pillars:

| Pillar             | Metric | Formula                                         | Meaning                              |
|--------------------|--------|-------------------------------------------------|--------------------------------------|
| Performance        | EL     | $(T_{actual} - T_{baseline}) / T_{baseline}$    | Efficiency vs baseline               |
|                    | D      | $\frac{1}{N}\sum d_i$                           | Avg. action duration                 |
| Interaction        | F      | $N / (T/60)$                                    | Interactions per minute              |
| Human-Centeredness | HCL    | $1 - \overline{RT}/RT_{max}$                    | Proxy for cognitive load             |
| Trust              | Tr     | $1 - errors/N$                                  | Proxy for acceptance of AI           |
| Adaptability       | A      | $(Acc_{late} - Acc_{early})/Acc_{early}$        | Improvement across session           |
| Similarity         | S      | Overlap between `probs` and `surrogate_probs` OR action match rate | Fidelity of surrogate |

**Example Metric Output:**

```json
{
    "metrics": {
        "F": 3.5,
        "D": 1.0,
        "HCL": 0.76,
        "Tr": 0.92,
        "A": 0.50,
        "S": 0.88,
        "EL": 0.20
    }
}
```

## 3. End-to-End Flow

```mermaid
flowchart LR
        A[decisions.json (pilot log)] --> B(compute_metrics)
        B --> C[metrics.json (results)]
        C --> D[Dashboard / Reporting]
```

## 4. Versions

- **Simulator version:** `sim-0.1.0`
- **Schema version:** `log-v1`

Every log and metrics file is stamped with version fields for traceability.
