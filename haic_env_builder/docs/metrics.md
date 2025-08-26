# HAIC Metrics — Definitions & Examples (sim-0.1.0)

This document defines the metrics computed by the simulator, so pilots know what to log and how results are derived.

## Notation

A run produces a sequence of `decisions`:

```json
[
  { "t": 0.0, "agent": "RadiologistAssistant", "action": "classify", "latency_ms": 420, "correct": true },
  ...
]
```

Let:

- `T`: total wall time of the session in seconds
- `N`: total number of interaction events (`len(decisions)`)
- `human_events`: events where `actor_type == "human"` (optional; otherwise infer by `actor_role`)
- `ai_events`: events where `actor_type == "ai"`
- `errors`: number of events with `correct == false` or `event_type == "error"`

> **Important**: If your logging cannot provide a field, the metric is either skipped or computed with a fallback (documented below).

---

## Metrics

### 1. Interaction Frequency (F)

**What:** Interactions per minute.

**Formula:**
```math
F = \frac{N}{(T / 60)}
```

Where:

- `F`: Interaction Frequency (events per minute)
- `N`: Total number of events
- `T`: Total session time in seconds

**Inputs required:**

- `t` timestamps for first/last event, or explicit `T`
- If `T` missing, approximate as `T = (t_last - t_first)`

**Range:** \([0, \infty)\) — higher means denser interaction.

**Example:**  
`N = 30` events, `T = 600s` → `F = 3.0` events/min.

---

### 2. Interaction Duration (D)

**What:** Mean atomic action duration (sec).

**Formula:**
```math
D = \frac{1}{N} \sum_{i=1}^{N} d_i
```

Where:

- `D`: Mean interaction duration (seconds)
- `N`: Number of actions
- `d_i`: Duration of the i-th action (seconds)

Where \(d_i\) is the duration of the \(i\)-th action (in seconds).
Where each \(d_i\) is:

- Prefer `duration_s` if logged.
- Else, derive from per-step timestamps (event i to i+1) for same actor.
- Else, use `latency_ms` (converted to sec) if present.

**Example:**
Five actions with `duration_s`: [0.8, 1.0, 1.1, 0.9, 1.2] → `D = 1.0s`.

---

### 3. Human Cognitive Load (HCL)

**What:** Proxy via response times; lower response time → lower load.

**Formula:**

```math
HCL = 1 - \frac{\overline{RT}}{RT_{max}}
```
Where:

- \( \overline{RT} \): mean human response time (sec)
- \(RT_{max}\): Maximum response time considered (default: 5 seconds; configurable)

**Range:** \([0, 1]\) (clamped)

**Example:**  
Mean RT = 1.2s, \(RT_{max} = 5s\) → \(HCL = 0.76\).

---

### 4. Trust Proxy (Tr)

**What:** Less error → higher trust.

**Formula:**
```math
Tr = 1 - \frac{errors}{N}
```

**Inputs required:**

- `correct: true/false` per event, OR `event_type: "error"`

**Range:** \([0, 1]\) (clamped)

**Example:**  
`errors = 3`, `N = 40` → \(Tr = 0.925\).

---

### 5. Adaptability (A)
**What:** Improvement of performance over time.

**Formula:**

**Formula:**  
```math
A = \frac{acc_{late} - acc_{early}}{\max(1, acc_{early})}
```

Where `acc_early` is accuracy in the first k events (default k = 20% of N) and `acc_late` in the last k events.

**Range:** \((-\infty, +\infty)\) — positive means improving.

**Example:**  
Early acc = 0.60, Late acc = 0.75 → \(A = 0.25\).

---

### 6. Surrogate Similarity (S)

**What:** Similarity between human policy and surrogate policy.

**Formula (soft):**

```math
S = \exp\left(-D_{KL}(P_{human}\,\|\,P_{sur})\right)
```

Where \(D_{KL}\) is the Kullback-Leibler divergence between the human's action distribution (\(P_{human}\)) and the surrogate's (\(P_{sur}\)).  
If only action labels (no probabilities), use simple overlap:

```math
S = \frac{\#\text{matching actions}}{N_{compare}}
```

**Range:** \([0, 1]\)

**Example:**  
80 matches out of 100 → \(S = 0.8\).

---

### 7. Effort / Efficiency Loss (EL)
**What:** Overhead vs. a task baseline.

**Formula:**
```math
EL = \frac{T_{actual} - T_{baseline}}{T_{baseline}}
```

Where \(T_{baseline}\) is the best-known or scripted time.

**Range:** \([0, \infty)\) (clamped at 0 when negative)

**Example:**  
\(T_{actual}= 540s\), \(T_{baseline}= 480s\) → \(EL = 0.125\) (12.5% slower).

---

## Required Logging Fields (minimal)

To compute all metrics reliably, log each `decision` with:

```json
{
  "t": 123.45,                     // seconds from session start
  "agent": "RadiologistAssistant", // id or name
  "actor_type": "ai",              // "human" | "ai"
  "action": "classify",            // symbolic action label
  "latency_ms": 420,               // optional; used for D / HCL
  "duration_s": 0.95,              // optional; preferred for D
  "correct": true,                 // used for Trust & Adaptability
  "probs": { "classify": 0.8, "highlight": 0.2 } // optional; for S
}
```

Session-level:

```json
{
  "task": "CT Scan Diagnosis",
  "T": 600.0,                  // optional if t-first/last exist
  "baseline_s": 480.0,         // for EL
  "seed": 42,                  // reproducibility
  "config_hash": "0dfea8ce2f90",
  "version": "sim-0.1.0"
}
```