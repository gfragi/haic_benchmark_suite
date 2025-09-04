# Metrics Explained

This document explains the **quantitative metrics** computed by the **HAIC Benchmark Suite**.
Metrics are grouped according to the framework pillars defined in our review paper: **Performance, Interaction, Human-Centeredness, Trust, Adaptability, Similarity**.

Each metric includes:

- **Formula** (mathematical definition)
- **Meaning** (what it tells us about Human–AI collaboration)
- **Example** (toy numbers for intuition)
- **Pilot Data Required** (what needs to be logged)

---

## Core HAIC Metrics

> **Core HAIC Metrics v1 are implemented in `metrics_core` (single source).**

## 1. Performance / Efficiency

### **Efficiency / Latency (EL)**

- **Formula:**

```math
  EL = \frac{T_{\text{actual}} - T_{\text{baseline}}}{T_{\text{baseline}}}
```

- **Meaning:** Measures extra time needed compared to a baseline. Lower is better.
- **Example:** If baseline task = 100s, actual = 120s → \( EL = 0.20 \) (20% slower).
- **Data Required:** Task start/end timestamps.

### **Mean Duration (D)**

- **Formula:**

  ```math
  D = \frac{1}{N} \sum_{i=1}^{N} d_i
  ```

- **Meaning:** Average duration per interaction.
- **Example:** Durations = [0.9, 1.1, 1.0]s → \( D = 1.0s \).
- **Data Required:** Per-decision `duration_s` or `latency_ms`.

---

## 2. Interaction / Collaboration

### **Interaction Frequency (F)**

- **Formula:**

  ```math
  F = \frac{N}{T/60}
  ```

- **Meaning:** How dense the collaboration is (# interactions per minute).  
- **Example:** 30 events in 10 minutes → \( F = 3.0 \) interactions/min.  
- **Data Required:** Decision timestamps (`t`).  

---

## 3. Human-Centeredness

### **Cognitive Load Proxy (HCL)**

- **Formula:**

  ```math
  HCL = 1 - \frac{\overline{RT}}{RT_{\max}}
  ```

- **Meaning:** Faster human response times → lower cognitive load.  
- **Example:** Avg RT = 1.2s, \( RT_{\max} = 5s \) → \( HCL = 0.76 \).  
- **Data Required:** Human `latency_ms` or `duration_s`.  

---

## 4. Trust

### **Trust Proxy (Tr)**

- **Formula:**

  ```math
  Tr = 1 - \frac{\text{errors}}{N}
  ```

- **Meaning:** High trust = few overrides/errors relative to total AI suggestions.
- **Example:** 3 errors in 40 interactions → \( Tr = 0.925 \).
- **Data Required:** Decision field `correct` or `event_type`.

---

## 5. Adaptability

### **Adaptability (A)**

- **Formula:**

  ```math
  A = \frac{Acc_{\text{late}} - Acc_{\text{early}}}{Acc_{\text{early}}}
  ```

- **Meaning:** Measures improvement across the session. Positive → learning/adaptation.  
- **Example:** Early accuracy = 0.6, late accuracy = 0.9 → \( A = 0.5 \).  
- **Data Required:** Decisions with correctness labels over time.  

---

## 6. Similarity

### **Surrogate Similarity (S)**

**Option 1 – Probability overlap:**

```math
S = \frac{1}{M} \sum_{i=1}^{M} \sum_{a} \min\big(p_i(a), q_i(a)\big)
```

where \( p_i \) = human probability distribution, \( q_i \) = surrogate distribution.

**Option 2 – Action match:**

```math
S = \frac{\#\{\text{matching actions}\}}{\#\{\text{compared actions}\}}
```

- **Meaning:** How well surrogate agent replicates human actions.
- **Example:** Human vs surrogate distributions overlap = 0.9 → \( S = 0.9 \).
- **Data Required:** `probs` vs `surrogate_probs`, or `action` vs `surrogate_action`.

### **Similarity (S)**

**Primary definition:**
When probability distributions (`probs` and `surrogate_probs`) are logged, Similarity is computed using a distributional overlap measure, such as Jensen–Shannon similarity.

**Fallback definition:**
If probability distributions are not available, but both `action` and `surrogate_action` are logged, Similarity is computed as a simple match rate:

```math
S = \frac{\text{\# of matching actions}}{\text{\# of compared actions}}
```

This approach ensures the metric is always computable—even when only categorical actions are logged.

---

| **Pillar**                      | **Metric** | **Formula**                                                           | **Range**                         | **Meaning / Story**                                                              |
| ------------------------------- | ---------- | --------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| **Performance / Efficiency**    | **EL**     | $(T_{actual} - T_{baseline}) / T_{baseline}$                          | $[0, +\infty)$. 0 = optimal       | Efficiency compared to baseline. High = slower, wasted effort.                   |
|                                 | **D**      | $\frac{1}{N}\sum d_i$                                                 | $[0, +\infty)$                    | Avg. action duration. Longer = bottlenecks. Balanced = smooth.                   |
| **Interaction / Collaboration** | **F**      | $N / (T/60)$                                                          | $[0, +\infty)$. Typical: 0–10/min | Interactions per minute. High = active collaboration, too high = inefficiency.   |
| **Human-Centeredness**          | **HCL**    | $1 - \overline{RT}/RT_{max}$                                          | $[0, 1]$                          | Proxy for human cognitive load. Higher = easier for humans, lower = heavy load.  |
| **Trust / Transparency**        | **Tr**     | $1 - \text{errors}/N$                                                 | $[0, 1]$                          | Proxy for trust in AI. High = humans accept AI, low = overrides/errors frequent. |
| **Adaptability**                | **A**      | $(Acc_{late} - Acc_{early})/Acc_{early}$                              | Usually $[-1, +1]$                | Improvement across session. Positive = adaptation, negative = degradation.       |
| **Similarity (Surrogates)**     | **S**      | Distribution overlap (probs vs surrogate\_probs) OR action match rate | $[0, 1]$                          | Fidelity of surrogate to human. High = faithful, low = unreliable.                      |



# Metrics Logging Specification

**Goal:** Make runs reproducible and critiques easy by logging exactly what each metric needs.

---

## 1) What to Log per Decision Row

Minimum fields each **decision/event** row should contain:

- **`t`** *(float, required)* — seconds since task start.
- **`agent`** *(string, required)* — stable agent id (e.g., `human1`, `ai1`).  
- **`actor_type`** *(string, required)* — `"human"` or `"ai"`.
- **`action`** *(string, required)* — action label.
- **`correct`** *(bool, recommended)* — whether the action was correct.  
- **`latency_ms`** *(float, optional)* — reaction time in **milliseconds** (prefer for human RT).  
- **`duration_s`** *(float, optional)* — action duration in **seconds** (use if `latency_ms` isn’t available).  
- **Optional surrogate fields**: `probs`, `surrogate_probs`, `surrogate_action` (for similarity metrics).


| Field            | Type   | Required | Description                                                              |
|------------------|--------|----------|--------------------------------------------------------------------------|
| `t`              | float  | ✔        | Timestamp (seconds since start of task).                                 |
| `agent`          | string | ✔        | Name/ID of the acting agent (human or AI).                               |
| `actor_type`     | string | ✔        | `"human"` or `"ai"`.                                                     |
| `action`         | string |    *recommended*    | Description of the action performed.                                     |
| `latency_ms`     | float  | ✔        | Reaction time in milliseconds (if available).                            |
| `duration_s`     | float  | ✔        | Duration of the action in seconds (alternative to latency).              |
| `correct`        | bool   | ✖        | Whether the action was correct (`true`/`false`).                         |
| `event_type`     | string | ✖        | `"error"`, `"override"`, `"success"`, etc.                               |
| `probs`          | dict   | ✖        | Probability distribution over actions for human decisions (optional).     |
| `surrogate_probs`| dict   | ✖        | Probability distribution over actions for surrogate agent (optional).     |
| `surrogate_action`| string| ✖        | Action taken by surrogate for comparison.                                |

> Tip: Keep units consistent (`latency_ms` in ms, `duration_s` in s).

---

## 2) Scenario Parameters (Once per Run)

These live in your scenario config / task parameters and must be present in the run payload:

- **`rt_max`** *(float, seconds)* — upper bound for typical human RT used by HCL.
- **`baseline_s`** *(float, seconds)* — baseline completion time used by Effort Loss (EL).

---

## 3) Common Quantities Defined

- **`T`** *(actual task time)* = `max(t) - min(t)` over all decisions (or `0` if fewer than 2 rows).
- **`RT (per decision)`**: for **human** rows, prefer `latency_ms / 1000`; if missing, use `duration_s` (seconds). Ignore non-positive or missing values when averaging.
- **`N`**: number of logged decisions (human + AI).  
- **`Nh`, `Na`**: counts for human / AI decisions (as needed).

---

## 4) Metric Definitions (Exact)

Below are each metric’s **definition**, **formula**, and **log dependencies**. All symbols refer to the fields above.

### F — Interaction Rate
- **Formula:** `F = N / (T / 60)`  *(interactions per minute)*
- **Needs:** `t` for `T`; count of rows for `N`.
- **Edge case:** If `T = 0`, set `F = 0`.

### D — Average Duration
- **Formula:** mean of per-row **duration (seconds)**.
- **Needs:** Prefer `duration_s`; if missing and `latency_ms` exists (AI actions), use `latency_ms / 1000`.
- **Edge case:** If no usable durations exist, report `null`.

### HCL — Human-Centeredness Proxy
- **Formula:** `HCL = 1 - (mean_human_RT / rt_max)` clamped to `[0, 1]`.
- **Needs:** Human RT per row (see *Common quantities*), and `rt_max` (seconds).
- **Edge case:** If no usable human RTs exist, report `null`.

### Tr — Trust Proxy
- **Formula:** `Tr = 1 - (errors / N)` where **errors** are rows with `correct = false`.
- **Needs:** `correct`.
- **Edge case:** If no correctness labels exist at all, report `null`.

### A — Adaptation (Early → Late)
- **Formula:** `A = (Acc_late - Acc_early) / Acc_early`.
- **Windowing Rule (default, index-based):**
  1. Order **human** decisions by `t`.
  2. Split into **early** = first **30%** and **late** = last **30%** by index.
  3. `Acc_*` = mean of `correct` (true = 1, false = 0) in each window.
- **Edge cases:**
  - Require ≥ **10** labeled human rows; else `A = null`.
  - If `Acc_early = 0` and `Acc_late > 0`, set `A = +∞` (or string `"inf"`); if both 0, `A = 0`.
  - If you prefer time-based windows (first/last 30% of `T`), keep that rule fixed and document it.

### S — Similarity (Human vs Surrogate)
Pick the best available signal, in this order:
1. **Action match rate:** `S = mean( action == surrogate_action )`.
2. **Distribution overlap:** `S = Σ_a min( probs[a], surrogate_probs[a] )`.
- **Needs:** Either `surrogate_action` per row, or both `probs` and `surrogate_probs`.
- **Edge case:** If neither signal exists, report `null`. Range `[0,1]`.

### EL — Effort Loss (Efficiency Gap to Baseline)
- **Formula:** `EL = max(0, (T - baseline_s) / baseline_s)`.
- **Needs:** `T`, `baseline_s`.
- **Edge case:** If `baseline_s` missing, `EL = null`. Higher EL ⇒ slower than baseline.

### EfficiencyScore — Convenience Index
- **Formula:** `EfficiencyScore = 1 / (1 + EL)`.
- **Needs:** `EL`.
- **Range:** `(0, 1]` (higher is better).

---

## 5) Missing Data Policy

- **No human RTs:** `HCL = null` (don’t guess).  
- **No correctness labels:** `Tr = null`, `A = null` (and `Acc_* = null`).  
- **No baseline:** `EL = null`, `EfficiencyScore = null`.  
- **Degenerate time:** If all `t` equal, `T = 0` ⇒ `F = 0`. EL still computable if `baseline_s` present.

---

## 6) Example Rows

**Human (labeled, with RT):**
```json
{ "t": 12.3, "agent": "human1", "actor_type": "human",
  "action": "confirm", "latency_ms": 850, "correct": true }
