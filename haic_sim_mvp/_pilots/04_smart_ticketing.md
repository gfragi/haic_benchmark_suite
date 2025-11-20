# README — Smart Ticketing (Active Learning) Environment & Logging

**Purpose.** This README explains how to integrate the Smart Ticketing Active Learning (AL) pilot with the HAIC Benchmarking Platform. It mirrors the structure used in the other pilots (Manufacturing, Healthcare).

---

## 0. What’s in this package

* **Environment config (JSON):** `smart_ticketing_al_env.json` — defines task/domain, agents, objects, and a demo `script` flow.
* **Sample bundle (JSON):** `smart_ticketing_al_sample.json` — one AL session with per-ticket interactions.

---

## 1. Environment Config (overview)

The environment config follows the shared schema used across pilots.

```json
{
  "sim_id": "pilot_st_al_v0",
  "environment": {
    "id": "ST_AL_ENV",
    "class": "base.Environment",
    "attributes": { "task": "active_learning_ticket_triage", "domain": "customer_support" }
  },
  "agents": [
    { "id": "ORCH", "class": "base.Agent", "model": "system",
      "affordances": ["start_run","notify","promote"] },
    { "id": "AL", "class": "base.Agent", "model": "ai",
      "affordances": ["sample_query","score_uncertainty","select_batch"] },
    { "id": "LAB", "class": "base.Agent", "model": "human",
      "affordances": ["label","correct","abstain"] },
    { "id": "MOD", "class": "base.Agent", "model": "ai",
      "affordances": ["train","predict","evaluate"] },
    { "id": "DEP", "class": "base.Agent", "model": "system",
      "affordances": ["deploy","rollback"] }
  ],
  "objects": [
    { "id": "Ticket", "class": "base.Object",
      "attributes": {"kind":"support_ticket"},
      "affordances": ["submit","label","triage"] },
    { "id": "Pool", "class": "base.Object",
      "attributes": {"kind":"unlabeled_pool"},
      "affordances": ["snapshot","update"] },
    { "id": "Sel", "class": "base.Object",
      "attributes": {"kind":"selection_batch"},
      "affordances": ["create"] },
    { "id": "DS", "class": "base.Object",
      "attributes": {"kind":"dataset"},
      "affordances": ["append","version"] },
    { "id": "Mdl", "class": "base.Object",
      "attributes": {"kind":"model"},
      "affordances": ["store","register"] }
  ],
  "script": [
    { "t": 0.0, "agent": "ORCH", "action": "start_run", "object": "Pool",
      "effect": {"pool_size": 12000, "class_proxy": {"billing":0.32,"tech":0.51,"other":0.17}} },
    { "t": 1.0, "agent": "AL", "action": "sample_query", "object": "Pool",
      "effect": {"strategy": "entropy", "k": 5, "budget_left": 500}, "latency_ms": 85 },
    { "t": 1.1, "agent": "AL", "action": "select_batch", "object": "Sel",
      "effect": {"ids": ["T001","T002","T003","T004","T005"], "utilities": [0.91,0.88,0.87,0.86,0.85]} },
    { "t": 2.0, "agent": "ORCH", "action": "notify", "object": "Sel",
      "effect": {"role":"labeler","method":"ui","batch_id":"BATCH_001"} },
    { "t": 15.0, "agent": "LAB", "action": "label", "object": "Ticket",
      "effect": {"ticket_id":"T001","label":"billing","confidence":0.9}, "duration_s": 18.0 },
    { "t": 16.5, "agent": "LAB", "action": "label", "object": "Ticket",
      "effect": {"ticket_id":"T002","label":"tech","confidence":0.8}, "duration_s": 22.0 },
    { "t": 18.0, "agent": "LAB", "action": "label", "object": "Ticket",
      "effect": {"ticket_id":"T003","label":"tech","confidence":0.85}, "duration_s": 17.0 },
    { "t": 19.5, "agent": "LAB", "action": "label", "object": "Ticket",
      "effect": {"ticket_id":"T004","label":"other","confidence":0.7}, "duration_s": 25.0 },
    { "t": 21.0, "agent": "LAB", "action": "label", "object": "Ticket",
      "effect": {"ticket_id":"T005","label":"billing","confidence":0.88}, "duration_s": 19.0 },
    { "t": 22.0, "agent": "MOD", "action": "train", "object": "Mdl",
      "effect": {"dataset_id":"ds_2025_11_17","added_labels":5}, "latency_ms": 12400 },
    { "t": 34.5, "agent": "MOD", "action": "evaluate", "object": "Mdl",
      "effect": {"metrics": {"f1_macro":0.782,"acc":0.84,"aupr":0.71}}, "latency_ms": 820 },
    { "t": 35.0, "agent": "DEP", "action": "deploy", "object": "Mdl",
      "effect": {"model_id":"mdl_st_42","version":"1.4.2","promote": true} }
  ]
}
```

Use the `script` as a demo or as a mapping guide for live events.

## 1.1 Sequence Diagram

```plaintextsequenceDiagram
autonumber
%% Smart Ticketing (Active Learning) — Pilot-side interactions only (with local logging + export)
actor LAB as Labeler (Human)
participant ORCH as ORCH (Orchestrator)
participant AL as AL (Active Learner)
participant POOL as Pool (Unlabeled)
participant SEL as Sel (Selection Batch)
participant MOD as MOD (Model/Trainer)
participant DEP as DEP (Deployer)
participant LOG as Log Buffer (Pilot)

note over ORCH,LOG: session_id minted at run start; interaction_id = ticket_id

ORCH->>POOL: start_run(pool_size, class_proxy)
ORCH-->>LOG: record pool_snapshot

AL->>POOL: sample_query(strategy, k, budget_left)
AL-->>ORCH: select_batch(ids[], utilities[])
AL-->>LOG: record al_query_issued (latency_ms)
AL-->>LOG: record al_candidates(batch_id, ids[], utilities[])

ORCH->>LAB: notify labelers (batch_id)
par For each ticket in batch
    ORCH->>LAB: label_request_sent(ticket_id)
    ORCH-->>LOG: record label_request_sent [interaction_id=ticket_id]
    LAB-->>ORCH: label_received(label, confidence) [duration_s]
    ORCH-->>LOG: record label_received [interaction_id=ticket_id]
end

AL->>MOD: model_update_started(dataset_id, added_labels)
AL-->>LOG: record model_update_started
MOD-->>AL: model_update_finished(metrics) [latency_ms]
AL-->>LOG: record model_update_finished

ORCH->>DEP: deployment_promoted(model_id, version, promote=true)
ORCH-->>LOG: record deployment_promoted

alt Abstain or low confidence
    LAB-->>ORCH: label_received(decision=abstain)
    ORCH-->>LOG: record label_received(abstain=true)
else Correction phase (optional)
    LAB-->>ORCH: correct(ticket_id, new_label)
    ORCH-->>LOG: record label_corrected
end

note over LOG: End of session → build JSON bundle for later upload (outside this diagram).
```

---

## 2. Data Model & IDs

* **sim_id**: app discriminator — e.g., `smart_ticketing_al` or `pilot_st_al_v0`.
* **session_id**: one AL run (keep stable for the whole cycle).
* **interaction_id**: one ticket (use `ticket_id`); propagate across all steps for that ticket.
* **actor_type**: `ai | human | system`.
* **action**: one of the event names in §3.
* **meta.task_parameters.rt_max**: SLA threshold (sec) for human label steps; default **60**.


## 2.1 Actors & Roles (who is who)
The main actors in the Smart Ticketing AL pilot are:

| ID   | Role / Responsibility                       | `actor_type` | Typical implementation (examples)                                   | Emits / handles these actions |
|------|---------------------------------------------|---------------|---------------------------------------------------------------------|-------------------------------|
| **ORCH** | Orchestrator for an AL run; coordinates pool snapshot, notifications, and promotion | `system`      | Node-RED flow, backend service, pipeline controller                 | `start_run`, `notify`, `deployment_promoted` |
| **AL**   | Active-learning selector; scores uncertainty and chooses a batch to label          | `ai`          | AL service (e.g., modAL/libact/Sklearn), custom selector microservice | `al_query_issued`, `al_candidates`, (reads pool) |
| **LAB**  | Human labeler/subject-matter expert; annotates tickets                             | `human`       | Annotator UI, internal tool                                         | `label_received`, `correct`, `abstain` (with `duration_s`) |
| **MOD**  | Model trainer/evaluator; updates model after new labels                            | `ai`          | Training pipeline (Kubeflow), job runner, notebook                  | `model_update_started`, `model_update_finished` (with `latency_ms`, metrics) |
| **DEP**  | Deployer/promoter; makes a trained model active in serving                         | `system`      | CI/CD step, model registry hook, KServe/Seldon deployer             | `deployment_promoted` (and optional `rollback`) |

### Objects (referenced in `objects[]`)
- **Ticket** (`support_ticket`): a single support request; maps to `interaction_id` (= `ticket_id`).
- **Pool** (`unlabeled_pool`): current unlabeled set seen by AL.
- **Sel** (`selection_batch`): the chosen ticket batch for labeling in this AL step.
- **DS** (`dataset`): labeled dataset/version used for training.
- **Mdl** (`model`): trained model artifact/registry entry.
---

## 3. Event Catalog (what to emit)

| Step                          | `actor_type` | `action`                | Must-have payload                            |
| ----------------------------- | ------------ | ----------------------- | -------------------------------------------- |
| Pool snapshot                 | `system`     | `pool_snapshot`         | `pool_size`, `class_proxy{...}`              |
| Issue AL query                | `ai`         | `al_query_issued`       | `strategy`, `k`, `budget_left`, `latency_ms` |
| Candidate batch               | `ai`         | `al_candidates`         | `batch_id`, `ids[]`, `utilities[]`           |
| Notify labeler                | `system`     | `label_request_sent`    | `batch_id`                                   |
| Label received *(per ticket)* | `human`      | `label_received`        | `label`, `confidence`, `duration_s`          |
| Model update start            | `ai`         | `model_update_started`  | `dataset_id`, `added_labels`                 |
| Model update done             | `ai`         | `model_update_finished` | `metrics{f1_macro,acc,...}`, `latency_ms`    |
| Deploy/promote                | `system`     | `deployment_promoted`   | `model_id`, `version`, `promote`             |

Per-ticket steps must carry **`interaction_id = ticket_id`**.

---

## 4. Session Bundle (canonical JSON)

Wrap events in a session bundle when posting to the Benchmarking API.

```json
{
  "logs": [{
    "sim_id": "smart_ticketing_al",
    "session_id": "st-al-20251117-001",
    "pilot_tag": "smart_ticketing",
    "user_id": "annotator_team_A",
    "app_version": "st_al_v1.0.0",
    "ai_model_version": "st-model-1.4.2",
    "meta": { "task_parameters": { "rt_max": 60 } },
    "decisions": [
      { "t": 0.0, "actor_type": "system", "action": "pool_snapshot",
        "payload": {"pool_size":12000,"class_proxy":{"billing":0.32,"tech":0.51,"other":0.17}} },
      { "t": 1.0, "actor_type": "ai", "action": "al_query_issued",
        "payload": {"strategy":"entropy","k":5,"budget_left":500}, "latency_ms": 85 },
      { "t": 1.1, "actor_type": "ai", "action": "al_candidates",
        "payload": {"batch_id":"BATCH_001","ids":["T001","T002","T003","T004","T005"],"utilities":[0.91,0.88,0.87,0.86,0.85]} },
      { "interaction_id":"T001", "t": 2.0, "actor_type": "system", "action": "label_request_sent",
        "payload": {"batch_id":"BATCH_001"} },
      { "interaction_id":"T001", "t": 15.0, "actor_type": "human", "action": "label_received",
        "payload": {"label":"billing","confidence":0.9}, "duration_s": 18.0 },
      { "interaction_id":"T002", "t": 2.0, "actor_type": "system", "action": "label_request_sent",
        "payload": {"batch_id":"BATCH_001"} },
      { "interaction_id":"T002", "t": 16.5, "actor_type": "human", "action": "label_received",
        "payload": {"label":"tech","confidence":0.8}, "duration_s": 22.0 },
      { "interaction_id":"T003", "t": 2.0, "actor_type": "system", "action": "label_request_sent",
        "payload": {"batch_id":"BATCH_001"} },
      { "interaction_id":"T003", "t": 18.0, "actor_type": "human", "action": "label_received",
        "payload": {"label":"tech","confidence":0.85}, "duration_s": 17.0 },
      { "interaction_id":"T004", "t": 2.0, "actor_type": "system", "action": "label_request_sent",
        "payload": {"batch_id":"BATCH_001"} },
      { "interaction_id":"T004", "t": 19.5, "actor_type": "human", "action": "label_received",
        "payload": {"label":"other","confidence":0.7}, "duration_s": 25.0 },
      { "interaction_id":"T005", "t": 2.0, "actor_type": "system", "action": "label_request_sent",
        "payload": {"batch_id":"BATCH_001"} },
      { "interaction_id":"T005", "t": 21.0, "actor_type": "human", "action": "label_received",
        "payload": {"label":"billing","confidence":0.88}, "duration_s": 19.0 },
      { "t": 22.0, "actor_type": "ai", "action": "model_update_started",
        "payload": {"dataset_id":"ds_2025_11_17","added_labels":5} },
      { "t": 34.5, "actor_type": "ai", "action": "model_update_finished",
        "payload": {"metrics":{"f1_macro":0.782,"acc":0.84,"aupr":0.71}}, "latency_ms": 13220 },
      { "t": 35.0, "actor_type": "system", "action": "deployment_promoted",
        "payload": {"model_id":"mdl_st_42","version":"1.4.2","promote": true} }
    ]
  }]
}
```

Fields per event: `interaction_id`, `t` *or* `timestamp`, `actor_type`, `action`, optional `duration_s`, optional `latency_ms`, optional `correct`, `payload{}`.

---

## 5. Producing logs from Node‑RED (sampler subflow)

* Drop the **Benchmarking Sampler** into your flow (same interface as other pilots):

  * Inputs: `msg.event_type`, `msg.source` (`ai|human|system`), `msg.payload{}`, optional `msg.latency_ms`, `msg.duration_s`, `msg.correct`, `msg.interaction_id`.
  * Flow context: holds `session_id` (mint once), batching buffer (5–50 events).
  * Output: batched POST to `/api/v1/logs` with header `x-api-key`.
* **Emit here:**

  1. After pool snapshot → `pool_snapshot`
  2. After AL query → `al_query_issued` and `al_candidates`
  3. On label requests → `label_request_sent` (per ticket)
  4. On annotator submission → `label_received` (per ticket, with `duration_s`)
  5. Around model update/eval → `model_update_started` / `model_update_finished` (with `latency_ms`)
  6. On deployment → `deployment_promoted`

---

## 6. Orchestration / Messaging hooks

* **MLOps/Training pipeline:** If you call an external trainer, wrap it with sampler events to capture timing and metrics.
* **RabbitMQ (optional bus):** Set an exchange (e.g., `co_create.st`), routing keys like `al.query`, `al.candidates`, `label.requested`, `label.received`, `model.updated`, `deploy.promoted`. Always propagate headers `session_id`, `interaction_id`.

---

## 7. Metrics mapping (dashboard)

| Metric                       | Source fields / computation                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **F (interactions/min)**     | Event count ÷ session window (minutes).                                                                            |
| **D (avg human duration)**   | Mean of `duration_s` on `label_received`.                                                                          |
| **HCL (human-centeredness)** | `1 − min(duration_s / rt_max, 1)` with `rt_max = 60`.                                                              |
| **Tr (trust/quality proxy)** | Acceptance/abstain rates; add `correct` when audits exist.                                                         |
| **EL (efficiency/latency)**  | `latency_ms` on `al_query_issued`, `model_update_finished`, plus end‑to‑end timings.                               |
| **AL KPIs**                  | Budget used (labels acquired/budget), mean `utilities` on `al_candidates`, Δmetrics after `model_update_finished`. |

**Fairness slices** (optional): group by `language`, `channel`, `priority`, `customer_tier`, `geo_bucket` (non‑PII).

---

## 8. Privacy & governance

* No PII in logs; bucketize user/customer attributes.
* Keep raw text in storage; logs carry pointers/IDs and summary metadata.
* Version models and runs; capture dataset/version IDs when training.

---

## 9. Validation & go‑live

* **Data quality:** unique `event_id` (if present), stable `session_id`, per‑ticket `interaction_id`, UTC timestamps.
* **Volume:** ≥1 session with ≥5 tickets to validate charts; later target ≥3 sessions and ≥2 app versions.
* **Reproducibility:** two runs of the same bundle ≤1% metric delta.
* **Ops:** zero P1 ingestion errors for 72h.

---

## 10. Quickstart

1. Import the Node‑RED **Benchmarking Sampler** subflow.
2. Configure `x-api-key`, endpoint `/api/v1/logs`, batching (5–50).
3. Emit events at the points in §5.
4. POST the sample bundle in this folder and verify the dashboard (Config 9).

---

## 11. Troubleshooting

* **Events not visible:** check `session_id` stability and wrapper `{ "logs": [ ... ] }`.
* **No fairness slices:** missing group fields (`language`, `priority`, …).
* **HCL flatlines:** set `meta.task_parameters.rt_max` (default 60).

---

## 12. Versioning

* **pilot_tag:** `smart_ticketing`
* **app_version:** semantic version or git SHA
* **ai_model_version:** model registry tag

**Last updated:**  2025-19-11 by gfragi
