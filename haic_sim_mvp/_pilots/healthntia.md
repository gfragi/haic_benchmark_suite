# Smart Healthcare (NS/Healthentia) Environment & Logging

Purpose. This README explains how to use the Neuro‑Symbolic (NS) Oncology environment config, how to emit logs compatible with the HAIC Benchmarking Platform, and how to wire Node‑RED/Kubeflow/RabbitMQ into the flow.


## 0. What’s in this package

- Environment config (JSON): `ns_healthentia_env.json` Defines task/domain, agents, objects, and a demo script.

- Sample bundles (JSON):
    - `ns_healthentia_sample_template.json` (2 interactions)
    - `ns_healthentia_stress_template.json` (1 session, 6 interactions)


## 2. Data Model & IDs

- **sim_id**: application discriminator — e.g., ns_healthentia or pilot_ns_v0.

- **session_id**: one clinician/engineer working session (login window or coherent task).
Tip: set once at session start; keep stable across all events in the run.

- **interaction_id**: one case/item (e.g., image_id). Propagate this across all steps for that item.
Fallback: if the upstream app lacks an ID, copy Node‑RED _msgid into interaction_id when the image enters the flow and reuse it downstream.

- **actor_type**: ai | human | system.

- **action**: one of the event names in §3.

- **meta.task_parameters.rt_max***: SLA threshold (sec) for human steps; default 30.

## 3. Event Catalog (what to emit per step)

1. `initial_input_provided` — image/data received
payload: `{ image_id, cohort{ cancer_type, stage }, site_id? }
`
2. `model_trained` or `ai_response` — model output
payload: `{ model_uri, metrics{...} }`, metrics: `latency_ms`

3. `xai_generated` — SHAP/LIME/etc. artifact
payload: `{ technique, top_features[], artifact_uri }`, metrics: `latency_ms`

4. `human_review_notified` — notification sent
payload: `{ role, presigned_url_id, method }`

5. `human_review_performed` — review outcome
payload: `{ decision: accept|reject, note }`, metrics: `duration_s`, optional: `correct`

6. `model_registered` — registry bookkeeping
payload: `{ model_id, version, registry }`

7. `error` — exceptions/timeouts
payload: `{ where, message, details }`



## 4. Session Bundle (canonical JSON)

Wrap events in a session bundle when sending to the Benchmarking API:

```json
{
"logs": [{
"sim_id": "ns_healthentia",
"session_id": "sess-20251017-NS001",
"pilot_tag": "healthcare_oncology",
"user_id": "expert_anon",
"app_version": "ns_v0.1.0",
"ai_model_version": "ns-2025-10-17",
"meta": { "task_parameters": { "rt_max": 30 } },
"decisions": [ /* events carrying interaction_id + action + timings */ ]
}]
}
```

Fields per event: `interaction_id`, `t` or `timestamp`, `actor_type`, `action`, optional `duration_s`, optional `latency_ms`, optional `correct`, `payload{}`.

## 5. Wiring Node-RED/Kubeflow/RabbitMQ

Drop the Benchmarking Sampler subflow into the flow (same interface as manufacturing):

- Inputs: `msg.event_type`, `msg.source` (`ai|human|system`), `msg.payload{}`, optional `msg.latency_ms`, `msg.duration_s`, `msg.correct`, `msg.interaction_id`.

- Flow context holds: `session_id`, batching buffer (5–50 events).

- **Output**: batched POST to `/api/v1/logs`.


**Where to emit:**

1. right after image ingest → initial_input_provided

2. after model finishes → model_trained (add latency_ms)

3. after XAI notebook step → xai_generated

4. on notification → human_review_notified

5. when review form is submitted → human_review_performed (add duration_s and correct if audited)

6. on registry write → model_registered


## 6. Metrics mapping (how the dashboard computes)

| Metric                       | Source fields / computation                                             |
| ---------------------------- | ----------------------------------------------------------------------- |
| **F (interactions/min)**     | Event count ÷ session window (minutes).                                 |
| **D (avg human duration)**   | Mean of `duration_s` on `human_review_performed`.                       |
| **HCL (human-centeredness)** | `1 − min(duration_s / rt_max, 1)` with `rt_max = 30`.                   |
| **Tr (trust proxy)**         | Acceptance vs. rejection rates; use `correct` on audited events.        |
| **EL (efficiency/latency)**  | `latency_ms` on `model_trained` + end-to-end timings between key steps. |
| **Fairness slices**          | Group metrics by `cancer_type`, `stage`, `site_id`, `age_bucket`.       |


