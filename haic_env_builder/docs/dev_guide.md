# HAIC Benchmark Suite – Developer Guide

This guide describes how to **log interactions**, how the **HAIC Benchmark Suite** computes metrics, and how pilots can ensure consistent and reproducible data collection.  
It combines three parts: **Pilot Handbook**, **Metrics Explained**, and **Log Schema**.

---

## 1. Pilot Handbook

This handbook defines how pilots should log interactions during Human–AI collaboration.
Logs are the **input** to the Benchmark Suite’s `compute_metrics()` function.

### 1.1 Log Schema

Each decision (interaction event) must be logged in **JSON** with the following fields:

| Field              | Type   | Required | Description                                                                 |
|--------------------|--------|----------|-----------------------------------------------------------------------------|
| `t`                | float  | ✔        | Timestamp (seconds since start of task).                                   |
| `agent`            | string | ✔        | Name/ID of the acting agent (human or AI).                                 |
| `actor_type`       | string | ✔        | `"human"` or `"ai"`.                                                       |
| `action`           | string | ✔        | Description of the action performed.                                       |
| `latency_ms`       | float  | ✖        | Reaction time in milliseconds (if available).                              |
| `duration_s`       | float  | ✖        | Duration of the action in seconds (alternative to latency).                |
| `correct`          | bool   | ✖        | Whether the action was correct (True/False).                               |
| `event_type`       | string | ✖        | `"error"`, `"override"`, `"success"`, etc.                                 |
| `probs`            | dict   | ✖        | Probability distribution over actions for human decisions (optional).      |
| `surrogate_probs`  | dict   | ✖        | Probability distribution over actions for surrogate agent (optional).      |
| `surrogate_action` | string | ✖        | Action taken by surrogate for comparison.                                  |

#### Example Log (`decisions.json`)

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

---

## 2. Metrics Explained

The Benchmark Suite computes quantitative metrics grouped by framework pillars defined in our review paper:
**Performance, Interaction, Human-Centeredness, Trust, Adaptability, Similarity.**

Each metric includes:

- **Formula** (mathematical definition)
- **Meaning** (interpretation in Human–AI collaboration)
- **Example** (toy values for intuition)
- **Data Required** (fields needed from the log)

### 2.1 Summary Table

| Pillar             | Metric                     | Formula (short)                | Meaning (short)                   | Example                        | Data Required                  |
|--------------------|---------------------------|--------------------------------|-----------------------------------|--------------------------------|-------------------------------|
| Performance        | Efficiency / Latency (EL) | (T<sub>act</sub>−T<sub>base</sub>)/T<sub>base</sub> | Extra time vs. baseline (↓ better) | 100s → 120s ⇒ 0.20 (20% slower) | Task start/end timestamps      |
|                    | Mean Duration (D)         | (1/N) ∑d<sub>i</sub>           | Avg duration per interaction      | [0.9, 1.1, 1.0] ⇒ 1.0s         | Per-decision latency/duration  |
| Interaction        | Interaction Frequency (F) | N/(T/60)                       | # interactions per minute         | 30 in 10 min ⇒ 3.0             | Decision timestamps            |
| Human-Centeredness | Cognitive Load Proxy (HCL)| 1−RT̄/RT<sub>max</sub>         | Faster RT ⇒ lower cognitive load  | Avg RT=1.2s, max=5s ⇒ 0.76      | Human latency/duration         |
| Trust              | Trust Proxy (Tr)          | 1−errors/N                     | Fewer overrides/errors ⇒ higher trust | 3 errors / 40 ⇒ 0.925      | Correctness / event type       |
| Adaptability       | Adaptability (A)          | (Acc<sub>late</sub>−Acc<sub>early</sub>)/Acc<sub>early</sub> | Improvement across session        | 0.6 → 0.9 ⇒ 0.5                | Correctness labels over time   |
| Similarity         | Surrogate Similarity (S)  | Option 1: prob. overlap<br>Option 2: action match | Human vs. surrogate behavior similarity | Overlap=0.9 ⇒ 0.9         | Probs or actions vs surrogate  |

### 2.2 Detailed Metric Definitions

#### Performance / Efficiency

- **Efficiency / Latency (EL)**
    ```math
    EL = (T_actual − T_baseline) / T_baseline
    ```
    Measures extra time needed vs baseline. Lower = better.

- **Mean Duration (D)**
    ```math
    D = (1/N) ∑ d_i
    ```
    Average duration per interaction.

#### Interaction

- **Interaction Frequency (F)**
    ```math
    F = N / (T / 60)
    ```
    Interactions per minute.

#### Human-Centeredness

- **Cognitive Load Proxy (HCL)**  
    ```math
    HCL = 1 − (RT̄ / RT_max)
    ```
    Faster human response times = lower cognitive load.

#### Trust

- **Trust Proxy (Tr)**

    ```math
    Tr = 1 − (errors / N)
    ```

    Few overrides/errors = higher trust.

#### Adaptability

- **Adaptability (A)**
    ```math
    A = (Acc_late − Acc_early) / Acc_early
    ```
    Positive values = improvement/learning across session.

#### Similarity

- **Surrogate Similarity (S)**
    - Option 1 – Probability overlap:
        ```math
        S = (1/M) ∑_i ∑_a min(p_i(a), q_i(a))
        ```
        Measures how well surrogate predicts human probabilities.
    - Option 2 – Action match:
        ```math
        S = #matching actions / #compared actions
    ```
    Measures how well surrogate replicates human actions.

### 2.3 Example Metric Output

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

---

## 3. Log Schema (Extended)

Logs represent decisions made during Human–AI collaboration and are the raw input for metric computation.

### 3.1 Example A – Radiologist scenario

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
```

### 3.2 Example B – Surrogate similarity with probabilities

```json
{
    "t": 5.0,
    "agent": "SurrogateAgent",
    "actor_type": "ai",
    "action": "suggest treatment",
    "probs": {"A": 0.7, "B": 0.2, "C": 0.1},
    "surrogate_probs": {"A": 0.65, "B": 0.25, "C": 0.1}
}
```

### 3.3 Example Full Run Artifact

```json
{
    "task": "CT Scan Diagnosis",
    "seed": 42,
    "config_hash": "0dfea8ce2f90",
    "decisions": [
        {
            "t": 0.0,
            "agent": "RadiologistAssistant",
            "actor_type": "ai",
            "action": "classifying CT scan",
            "latency_ms": 400,
            "duration_s": 0.9,
            "correct": true
        },
        {
            "t": 1.0,
            "agent": "HumanRadiologist",
            "actor_type": "human",
            "action": "accept AI suggestion",
            "latency_ms": 600,
            "duration_s": 1.2,
            "correct": true
        }
    ],
    "metrics": {
        "F": 5.2,
        "D": 1.0,
        "HCL": 0.76,
        "Tr": 0.95,
        "A": 0.1,
        "S": 0.85,
        "EL": 0.2
    },
    "status": "success",
    "timestamp": "2025-08-27T10:45:00Z"
}
```

---

## 4. End-to-End Flow

```mermaid
flowchart LR
        A[decisions.json (pilot log)] --> B(compute_metrics)
        B --> C[metrics.json (results)]
        C --> D[Dashboard / Reporting]
```

---

## 5. Versions

- Simulator version: `sim-0.1.0`
- Schema version: `log-v1`

Every log and metrics file is stamped with version fields for traceability.
