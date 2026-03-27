# Pilot Partner Guide — Why send logs & how to read the results (v1)

> A short, practical handout for pilot teams on **what to send**, **what you get back**, and **how to interpret** the metrics for your business.

---

## 1) The value you get

**In return for a lightweight JSON log**, you get a living dashboard with:

* **Latency SLAs**: AI p50/p90/p95 (ms) and Human p50/p90/p95 (s), with red guide-lines for agreed caps.
* **Agreement rate ("correct")** between AI and human decisions, trended over time.
* **Funnel**: Created → AI evaluated → Human verified.
* **Error-type Pareto** (top field/categories causing rework).
* **Fairness slices** (optional): compare metrics by site, priority, user group, etc.

These views translate directly to business goals: **faster resolution**, **fewer escalations**, **more automation**, **better user/operator experience**.

---

## 2) What to send (minimal)

No schema change is needed if you already log the items below.

**Per decision/event** (one line per step):

* `timestamp` (ISO8601 with timezone)
* `actor_type` (`ai` | `human`)
* `action` (e.g., `application_created`, `ai_evaluated`, `operator_verified` …)
* **Timing**: `latency_ms` (for AI steps) or `duration_s` (for human steps) — if applicable
* `interaction_id` (ID of the case/ticket/application/job)
* `payload` (free-form, include decisions such as `ai_decision`, `op_decision`, `*_fields_with_error` arrays if you have them)

**Per upload/session** (top-level fields):

* `pilot_tag` (e.g., `applications`, `manufacturing`)
* `app_version` (if relevant)
* `ai_model_version`
* `session_started_at` / `session_ended_at` (ISO8601 timestamps for the batch/session)
* *(Optional)* `extras.rt_limits`: `{ "rt_max_ai_ms": 20000, "rt_max_human_s": 30 }`
* *(Optional but recommended)* `extras.derive_correct_rules` (see §5)



---

## 3) What we compute automatically

### Core interaction metrics

* **F (Interactions/min)**: How much work gets done per minute.
* **D (Avg action duration)**: Mean of `duration_s`/`latency_ms` for atomic steps.
* **HCL (Human‑centeredness)**: Higher when mean human response is well within `rt_max_human_s`.
* **Tr (Trust proxy)**: 1 − error rate among labeled/explicit error events.
* **A (Adaptability)**: Trend in correctness early vs late in a session (tanh‑bounded).
* **S (Surrogate similarity)**: Agreement with surrogate/assist actions if provided (or action match fallback).
* **EL (Effort loss vs baseline)**: Extra time vs a reference baseline.
* **EfficiencyScore**: Composite shaped by EL and gentle off‑role/progress signals.

### Extended metrics (when data exists)

* **Effectiveness**: Prediction Accuracy, Precision, Recall, Overall System Accuracy, Model Improvement Rate.
* **Efficiency**: Response Time, Teaching Query Efficiency, Resource Utilization, Task Completion Time, Correction Efficiency, Error Reduction, Knowledge Retention.
* **Adaptability & Learning**: Feedback Impact, Adaptability Score, Impact of Corrections, Learning Efficiency, Objective Fulfilment Rate.
* **Collaboration**: Human‑AI Agreement Rate, AI Assistance Rate, Decision Effectiveness, Time to Resolution, Human Effort Saved.
* **Trust & Safety**: Confidence, Trust Score, Safety Incidents, System Reliability.
* **Robustness**: Adversarial Robustness, Domain Generalization.

---

## 4) How to read them (business interpretation cheat‑sheet)

| Metric                   | If HIGH                  | If LOW               | Typical action                                           |
| ------------------------ | ------------------------ | -------------------- | -------------------------------------------------------- |
| **AI p95 latency**       | Within SLA → capacity OK | Breaches SLA         | Profile hotspots; batch/async; cache; model/infra tuning |
| **Human p95 response**   | Within SLA → stable ops  | Above cap            | Simplify UI; better triage; cut handoffs; align staffing |
| **Agreement (correct)**  | Reliable automation      | Disagreement pockets | Tighten rules; improve XAI; clarify instructions         |
| **Funnel pass‑through**  | Healthy pipeline         | Drop‑offs            | Fix specific stage; reduce rework loops                  |
| **Error Pareto**         | Few dominant categories  | Many small causes    | Fix top 2–3 fields → largest impact                      |
| **HCL**                  | Smooth human flow        | Drag/friction        | UX tweaks; training; guidance tooling                    |
| **EL / EfficiencyScore** | Lean operations          | Waste/overhead       | Remove off‑role steps; streamline recipe                 |
| **A (Adaptability)**     | Learning from feedback   | Stagnation           | Revisit AL strategy; sampling; labeling                  |

---

## 5) How we derive **correct** (so you don’t have to)

You can let us compute `correct` from your own business rules. Example mapping:

```json
{
  "derive_correct_rules": [
    { "when": { "ai_decision": "Accepted" }, "set": true },
    { "when": { "ai_decision": "Flagged for verification", "op_decision": "Accepted after verification" }, "set": true },
    { "when": { "ai_decision": "Flagged for verification", "op_decision": "Rejected after verification" }, "set": false },
    { "when": { "ai_decision": "Rejected", "op_decision": "Fixed and accepted" }, "set": true },
    { "when": { "ai_decision": "Rejected", "op_decision": "Rejected" }, "set": true },
    { "when": { "ai_decision": "Rejected", "op_decision": "Accepted" }, "set": false }
  ]
}
```

Place it under `extras.derive_correct_rules` in the uploaded JSON **or** share it once and we’ll apply it during evaluation.

---

## 6) Visuals you’ll see on the dashboard

* **Latency bars** (AI & Human): p50/p90/p95 with SLA lines.
* **Agreement stack** by week (Accepted, Flagged→Accepted/Rejected, Rejected→… outcomes).
* **Funnel** (Created→AI→Human) with pass‑through rates.
* **Error‑type Pareto** (e.g., top fields causing rejections/flags).
* **Fairness slices** (optional cohorts: site, channel, priority…).

---

## 7) Minimal example (single application)

```json
{
  "sim_id": "pilot_apps_v1",
  "session_id": "batch_2026-Q1",
  "pilot_tag": "applications",
  "app_version": "apps_v1.0.0",
  "ai_model_version": "novo-2025-12",
  "extras": { "rt_limits": { "rt_max_ai_ms": 20000, "rt_max_human_s": 30 } },
  "decisions": [
    {
      "interaction_id": "APP_000473",
      "timestamp": "2026-01-31T20:58:02Z",
      "actor_type": "human",
      "action": "application_created",
      "duration_s": 12.4,
      "payload": { "role": "citizen" }
    },
    {
      "interaction_id": "APP_000473",
      "timestamp": "2026-01-31T20:58:17Z",
      "actor_type": "ai",
      "action": "ai_evaluated",
      "latency_ms": 14850.2,
      "payload": { "ai_decision": "Flagged for verification", "ai_fields_with_error": ["ADDRESS","POWER_SUPPLY"] }
    },
    {
      "interaction_id": "APP_000473",
      "timestamp": "2026-02-01T08:31:03Z",
      "actor_type": "human",
      "action": "operator_verified",
      "duration_s": 73.4,
      "payload": { "op_decision": "Accepted after verification" }
    }
  ]
}
```

---

## 8) Onboarding in 3 steps

1. **Export** your current logs as JSON (one file per batch) with the fields in §2.
2. **Upload** via the provided endpoint/UI (filenames auto‑timestamped).
3. **Open the dashboard** — the views above render automatically.

> Optional: include `derive_correct_rules` in the JSON; otherwise we can keep it centrally.

---

## 9) FAQ

* **What if there’s no operator step?** We derive `correct` from AI outcome where your rules say it’s safe (e.g., `Accepted` ⇒ `true`).
* **Privacy/security?** Logs stay in the project storage (MinIO). We only read the fields you send and do not need personal data; please redact where possible.
* **Can we customize SLAs/thresholds?** Yes — set `extras.rt_limits` per batch or agree centrally.

---

**Contact:** George F. — HAIC Benchmarking
