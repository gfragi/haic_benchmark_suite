# Metrics Explained

This document explains the **quantitative metrics** computed by the **HAIC Benchmark Suite**.
Metrics are grouped according to the framework pillars defined in our review paper: **Performance, Interaction, Human-Centeredness, Trust, Adaptability, Similarity**.

Each metric includes:

- **Formula** (mathematical definition)
- **Meaning** (what it tells us about Human–AI collaboration)
- **Example** (toy numbers for intuition)
- **Pilot Data Required** (what needs to be logged)

---

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

## 7. End-to-End Flow

```text
[Placeholder for pipeline / process flow]
