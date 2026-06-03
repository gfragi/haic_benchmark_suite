# Smart Ticketing — Evaluation Onboarding & Integration Guide (v1)

## Purpose

This document describes how the Smart Ticketing pilot integrates with the HAIC Benchmarking Platform in a simple, repeatable, and non-intrusive way. The goal is to evaluate AI-assisted workflows without changing your business logic or internal data structures.

## 1. What we are jointly trying to achieve

We aim to:

- Evaluate AI performance, human effort, and collaboration quality
- Compare results over time, per model version, and per application version
- Enable continuous evaluation as more data becomes available

This is done by:

- Agreeing once on a shared environment vocabulary
- Mapping your existing logs to this vocabulary
- Importing logs and computing metrics automatically

## 2. High-level integration flow

### Pilot workflow description
You explain how Smart Ticketing works in plain language.

### Environment agreement (semantics)
We agree on actors, objects, and canonical actions ("affordances").

### Log structure agreement
We align on the minimum fields required in logs.

### Sample validation
You send a small sample → we validate and confirm compatibility.

### Continuous evaluation
As more sessions are logged, metrics and comparisons update automatically.

**Important:** Your payload remains pilot-owned. We store it, but we do not enforce or interpret its internal structure.

## 3. Pilot workflow (example)

Example Smart Ticketing flow:

- Citizen submits an application
- AI evaluates the application
- Operator verifies the application (only when needed)

This workflow may include:

- Applications never reviewed by an operator
- Applications corrected and accepted
- Applications rejected

All of these paths are supported.

## 4. Environment contract (shared vocabulary)

### 4.1 Actors (who acts)

| Actor type | Description |
|------------|-------------|
| human | Citizen or operator |
| ai | AI / Active Learning model |
| system | Ticketing platform / workflow engine |

### 4.2 Objects (what is acted upon)

| Object | Meaning |
|--------|---------|
| application | A single ticket / request / case |

### 4.3 Canonical affordances (what happens)

These are canonical actions used only for evaluation and comparison.

| Affordance | Description |
|------------|-------------|
| application_created | Citizen submits application |
| ai_evaluated | AI evaluates the application |
| human_review_performed | Operator reviews the application |

Your internal action names do not need to match these.

### 4.4 Action mapping

Your logs may contain actions like:

- citizen_submit
- auto_check
- operator_validate

We define a simple mapping:

```json
{
  "citizen_submit": "application_created",
  "auto_check": "ai_evaluated",
  "operator_validate": "human_review_performed"
}
```

This mapping is agreed once and reused.

## 5. Log structure (what we expect in logs)

### 5.1 Log organization

Logs may be split across files or merged

One upload may contain one or many sessions

The platform handles merging internally

### 5.2 Required fields per event

Each event ("decision") should include:

```json
{
  "interaction_id": "APP_000473",
  "timestamp": "2026-01-10T07:02:44+00:00",
  "actor_type": "human | ai | system",
  "action": "pilot_native_action_name",
  "payload": { "...": "free-form" }
}
```

### 5.3 Timing fields (critical for metrics)

| Event type | Field | Meaning |
|------------|-------|---------|
| AI action | latency_ms | AI runtime |
| Human action | duration_s | Human effort |



### 5.4 Context fields (recommended)

At session or event level:

- sim_id
- session_id
- pilot_tag
- ai_model_version
- app_version

These enable comparisons but are not mandatory for validation.

## 6. "Correct" / agreement derivation

You do not need to send a correct field.

We derive it using agreed rules, for example:

```json
[
  { "when": { "ai_decision": "Accepted" }, "set": true },
  { "when": { "ai_decision": "Flagged", "op_decision": "Accepted" }, "set": true },
  { "when": { "ai_decision": "Flagged", "op_decision": "Rejected" }, "set": false }
]
```

This logic is:

- Pilot-defined
- Transparent
- Adjustable if business logic changes

## 7. Sample validation (first milestone)

What we ask from you:

- One sample log file
- 10–50 applications
- Includes at least:
  - One operator-reviewed case
  - One non-reviewed case

What you get back:

- Validation report
- First metrics
- Confirmation that the pipeline works

## 7. Metrics mapping (core dashboard – v1)

This section defines the core metrics that are computed in the current platform version. All metrics are derived only from logged events and timing fields, without assumptions about business logic.

Percentiles (p50 / p90 / p95) and advanced distributions will be added in a later iteration.

### 7.1 Interaction & Activity Metrics

| Metric | Meaning | Source / Computation |
|--------|---------|----------------------|
| F — Interaction Frequency | How active the system is | (# agent events) ÷ (session duration in minutes) |

**Notes:**

- Counts human + AI + system actions
- Uses first and last timestamps in a session (no explicit session start required)

### 7.2 Human-Centered Metrics

| Metric | Meaning | Source / Computation |
|--------|---------|----------------------|
| D — Average Human Duration | Mean human effort per action | Mean of duration_s on human actions |
| HCL — Human-Centeredness Level | How manageable the system is for humans | 1 − min(mean(duration_s) / rt_max_human_s, 1) |

**Defaults:**

- rt_max_human_s = 60 (configurable per pilot)

**Interpretation:**

- HCL → 1 : low human effort
- HCL → 0 : high cognitive or operational load

### 7.3 Trust / Quality Proxy Metrics

| Metric | Meaning | Source / Computation |
|--------|---------|----------------------|
| Tr — Trust proxy | Agreement & outcome quality | Derived from acceptance / rejection patterns |
| Correct (derived) | Agreement label (optional) | Derived from pilot-defined rules (not required in logs) |

**Notes:**

- correct is not mandatory
- When available, it improves Trust and Adaptability metrics
- When missing, Tr is computed from observable decisions only

### 7.4 Efficiency & Latency Metrics

| Metric | Meaning | Source / Computation |
|--------|---------|----------------------|
| EL — Efficiency / Latency | AI-side efficiency cost | Mean latency_ms on AI actions |
| End-to-end latency (basic) | Workflow responsiveness | Δ timestamps between key actions |

**Notes:**

- Uses existing latency_ms
- Does not require session start/end fields
- Percentiles will be introduced later

### 7.5 Active Learning (AL) Core KPIs

| Metric | Meaning | Source / Computation |
|--------|---------|----------------------|
| Label budget usage | Human effort spent | labels_acquired ÷ budget |
| Utility (mean) | Value of queried samples | Mean utilities on AL candidate events |
| Δ Performance (trend) | Learning improvement | Difference before/after model_update_finished |

**Notes:**

- Metrics are computed when corresponding events exist
- Missing AL fields do not break evaluation

### 7.6 Important clarification

Metrics are event-driven, not schema-driven

Missing fields → metric is skipped, not failed

Payload structure is pilot-owned

Only actor_type, action, timestamp, and timing fields are required

### 7.7 Metrics roadmap

The following will be added once the backend support is finalized:

- Latency percentiles (p50 / p90 / p95)
- Distribution plots
- SLA violation rates
- Cross-pilot normalized benchmarks

**Key message to pilots**

If you log who acted, what happened, and how long it took, the platform can already compute meaningful metrics.

## 9. Continuous evaluation (what happens next)

Once validation succeeds:

- You periodically export logs
- We import and compute updated results
- You can track improvements and regressions

No re-integration needed unless:

- New actions are introduced
- Workflow semantics change

## 10. Next concrete actions

Jointly agreed next steps:

- Confirm environment contract (Actors, Objects, Affordances)
- Confirm action mapping
- Send first sample log
- Review validation results together
- Start continuous evaluation

## Final note

This process is designed to:

- Respect pilot autonomy
- Minimize integration effort
- Produce results that are meaningful for business, technical, and operational stakeholders
