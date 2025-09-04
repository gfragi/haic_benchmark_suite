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

| **Pillar**                      | **Metric** | **Formula**                                                           | **Range**                         | **Meaning / Story**                                                              |
| ------------------------------- | ---------- | --------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| **Performance / Efficiency**    | **EL**     | $(T_{actual} - T_{baseline}) / T_{baseline}$                          | $[0, +\infty)$. 0 = optimal       | Efficiency compared to baseline. High = slower, wasted effort.                   |
|                                 | **D**      | $\frac{1}{N}\sum d_i$                                                 | $[0, +\infty)$                    | Avg. action duration. Longer = bottlenecks. Balanced = smooth.                   |
| **Interaction / Collaboration** | **F**      | $N / (T/60)$                                                          | $[0, +\infty)$. Typical: 0–10/min | Interactions per minute. High = active collaboration, too high = inefficiency.   |
| **Human-Centeredness**          | **HCL**    | $1 - \overline{RT}/RT_{max}$                                          | $[0, 1]$                          | Proxy for human cognitive load. Higher = easier for humans, lower = heavy load.  |
| **Trust / Transparency**        | **Tr**     | $1 - \text{errors}/N$                                                 | $[0, 1]$                          | Proxy for trust in AI. High = humans accept AI, low = overrides/errors frequent. |
| **Adaptability**                | **A**      | $(Acc_{late} - Acc_{early})/Acc_{early}$                              | Usually $[-1, +1]$                | Improvement across session. Positive = adaptation, negative = degradation.       |
| **Similarity (Surrogates)**     | **S**      | Distribution overlap (probs vs surrogate\_probs) OR action match rate | $[0, 1]$                          | Fidelity of surrogate to human. High = faithful, low = unreliable.               |

#### Narrative when taken together

- **F + D** → How much and how long do humans & AI interact?

- **HCL** → How costly is it for the human (effort)?

- **Tr** → How much do humans trust the AI?

- **A** → Do they adapt together over time?

- **S** → Can surrogates stand in for humans?

- **EL** → Is the collaboration efficient?

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

![End-to-End Flow](fig_diagrams/end-to-end%20flow.png)

## 4. Versions

- **Simulator version:** `sim-0.1.0`
- **Schema version:** `log-v1`

Every log and metrics file is stamped with version fields for traceability.
