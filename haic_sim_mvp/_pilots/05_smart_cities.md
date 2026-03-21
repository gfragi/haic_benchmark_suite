# HumAIne Smart City Pilot – Benchmarking & Simulation

> Version: 1.0 • Pilot tag: `smart_city` • Schema version: `1.0`
> Stack: FastAPI • MinIO • PostgreSQL • Vue/Chart.js • HAIC Env‑Builder

---

## 0. Purpose

This README specifies how the **Smart City Permit Screening** pilot plugs into the **HAIC Benchmarking & Simulation Suite** so we can: (a) simulate and ingest events, (b) compute common HAIC metrics (F, D, HCL, Tr, EL, fairness), (c) compare app versions, and (d) reproduce dashboards and reports consistently across pilots.

---

## 1. Pilot Overview

**Scenario:** Citizens submit permit applications. The system (AI) auto‑scans and either auto‑approves or flags an application. Flagged applications are reviewed by a human operator who approves or rejects. We measure system performance, human workload, trust/disagreement.

**Key actors & objects:**

* **SYS (AI)**: scans applications and outputs findings.
* **OP (Operator)**: reviews flagged items, provides structured reasons/decisions.
* **APP (Application)**: the permit request with identifying attributes.

---

## 2. Architecture & Data Flow

1. **Env‑Builder** runs scenarios with surrogate agents (SYS & OP) → emits **append‑only events**.
2. **FastAPI ingestion** validates events and writes to **MinIO**.
3. **Metrics Service** aggregates time windows → **compute_metrics()** returns HAIC metrics.
4. **Results Registry (Postgres)** stores the aggregate artifact `minio_path`, `pilot_tag`, `app_version`.
5. **Vue/Chart.js** renders comparisons and fairness slices.

---

 
    "operator_reason_codes": ["SURNAME_TYPO"],
    "operator_comments": "Surname typo; VAT ok after re-entry",
    "disagreement_with_system": true,
    "audit_type": "random"    
  }
}
```

### 3.2 Snapshot Shape (Materialized State)

```json
{
  "schema_version": "1.0",
  "application_id": "APP-2025-000123",
  "attributes": {
    "name":"Anna","surname":"Papadopoulou","father":"Giorgos",
    "id":"AB123456","address":"Eratosthenous 15, Athens",
    "license_plate":"XYZ1234","vat":"EL123456789","power_supply":"residential-single-phase"
  },
  "state": "approved",
  "created_on": "2025-11-10T09:40:00Z",
  "system": {
    "processed_on": "2025-11-10T09:42:11Z",
    "findings": ["surname","vat"],
    "comments": "Surname mismatch; VAT format issue",
    "confidence": 0.84,
    "random_audit_flag": true
  },
  "operator": {
    "operator_id": 1042,
    "process_begins": "2025-11-10T10:05:02Z",
    "duration_s": 220,
    "decision": "approved",
    "decision_code": "ACCEPT_MINOR_MISMATCH",
    "reason_codes": ["SURNAME_TYPO"],
    "comments": "Surname typo; VAT ok after re-entry"
  },
  "provenance": { "last_event_id": "uuid", "last_updated": "2025-11-10T10:08:42Z" }
}
```

### 3.3 Enums (Controlled Vocabularies)

* **`system_findings`**: `name`, `surname`, `father`, `id`, `address`, `license_plate`, `vat`, `power_supply`
* **`operator_decision_code`**: `REJECT_DATA_MISMATCH`, `REJECT_MISSING_DOCS`, `REJECT_FRAUD_SUSPECT`, `ACCEPT_MINOR_MISMATCH`, `ACCEPT_FORMATTING_FIX`, `ACCEPT_AFTER_DOC_UPLOAD`
* **`operator_reason_codes`**: `SURNAME_TYPO`, `VAT_FORMAT`, `ADDRESS_FORMAT`, `PLATE_OCR_ERROR`, `DOC_EXPIRED`, …
* **`audit_type`**: `random`, `targeted`, `escalation`

---

## 4. MinIO Layout

```
humaine/smart-city/
  events/YYYY/MM/DD/{application_id}/{timestamp}_{eventType}.json
  snapshots/{application_id}.json
  aggregates/daily/YYYY-MM-DD.json
```

---

## 5. API (FastAPI)

### 5.1 Ingestion

* `POST /events` → validate by `event_type`, write to MinIO
* `POST /snapshots/upsert` → materialize latest state per `application_id`

**Curl example**

```bash
curl -X POST http://localhost:8000/events \
  -H 'Content-Type: application/json' \
  -d @examples/event_system_scan.json
```

### 5.2 Metrics

* `POST /metrics/compute`
  **Body:** `pilot_tag`, `from`, `to`, `slices`, `app_version`

**Response (shape)**

```json
{
  "pilot_tag":"smart_city",
  "app_version":"v1.0.0",
  "window":{"from":"2025-11-10T00:00:00Z","to":"2025-11-10T23:59:59Z"},
  "metrics":{
    "F":0.72,
    "D":185.4,
    "HCL":0.81,
    "Tr":0.93,
    "EL":{"system_ms":4200,"e2e_ms":125000}
  },
  "fairness":{
    "by_power_supply":[
      {"group":"residential-single-phase","F":0.75,"D":170,"Tr":0.95},
      {"group":"industrial","F":0.61,"D":240,"Tr":0.88}
    ]
  },
  "findings_quality":{
    "surname":{"TP":48,"FP":7,"FN":5,"TN":140},
    "vat":{"TP":32,"FP":9,"FN":4,"TN":155}
  },
  "minio_path":"humai/smart-city/aggregates/daily/2025-11-10.json"
}
```

---

## 6. Environment (YAML)

```yaml
schema_version: 1.0
sim_id: smart_city_v1
environment:
  id: SMARTCITY_PERMITS
  class: base.Environment
  attributes: { task: "permit_screening", domain: "public_admin" }
agents:
  - id: OP
    class: base.Agent
    model: human
    affordances: [view, annotate, approve, reject]
  - id: SYS
    class: base.Agent
    model: ai
    affordances: [scan, explain]
objects:
  - id: APP
    class: base.Object
    attributes: { kind: "application" }
    affordances: [create, update]
policies:
  audit:
    random_rate: 0.10
    targeted_rules: ["low_confidence", "multi_findings>=2"]
  disagreement:
    p_minor_typo_accept: 0.35
    p_system_fp: 0.08
    p_system_fn: 0.06
logging:
  sink: minio
  base_path: humai/smart-city
  write: [events, snapshots, aggregates]
```

**Run**

```bash
POST /sim/run {"scenario_path":"./scenarios/smart_city_v1.yaml"}
```

---

## 7. Metric Mapping (compute_metrics)

* **F (interactions/min):** `len(events) / window_minutes`
* **D (avg human duration):** mean of `duration_s` over `OperatorReviewCompleted`
* **HCL (human-centeredness):** `1 − min((response_time_sec / (rt_max*60)), 1)` with `response_time_sec = process_begins − created_on` and `rt_max=30` minutes
* **Tr (trust proxy):** `1 − disagreement_rate`, where `disagreement_rate = count(disagreement_with_system)/count(OperatorReviewCompleted)`
* **EL (efficiency/latency):**

  * System: `system_processed_on − created_on`
  * End‑to‑End: `final_decision_time − created_on`
* **Fairness slices:** groupBy `power_supply`, geo bucket, time‑of‑day, etc.

### 7.1 Finding Quality (per field)

Use operator review as ground truth when present:

* **TP:** finding ∧ operator_reason confirms field
* **FP:** finding ∧ operator_decision_code ∈ `ACCEPT_*`
* **FN:** ¬finding ∧ operator rejected with matching reason
* **TN:** ¬finding ∧ operator approved without reasons

---

## 8. Expected Results (sanity targets)

These are **indicative targets** for a balanced simulation; adjust with scenario parameters.

* Auto‑approval rate (system): **60–75%**
* Escalation rate (`needs_attention`): **25–40%**
* Operator disagreement with system: **5–12%**
* Avg operator duration (D): **150–240s**
* Trust proxy (Tr): **≥ 0.88** in steady state
* Precision/Recall per field: **≥ 0.85 / ≥ 0.80** (surname, vat) in baseline
* Random audit yield (change rate): **1–4%**

Use these to check regression between `app_version`s.

---

## 9. Frontend (Vue/Chart.js)

* Reuse `VisualizationPage.vue` + `PlotChart.vue`.
* Slices: `power_supply`, time‑of‑day, weekday/weekend; comparative by `app_version`.
* Charts:

  * Bars for F, D, HCL, Tr, EL;
  * Stacked/grouped bars per slice;
  * Confusion bars (TP/FP/FN/TN) per finding.

---

## 10. Result Registration (Postgres)

```sql
INSERT INTO results (pilot_tag, app_version, created_at, minio_path, meta)
VALUES (
  'smart_city', 'v1.0.0', NOW(),
  'humai/smart-city/aggregates/daily/2025-11-10.json',
  '{"env":"SMARTCITY_PERMITS","schema_version":"1.0"}'::jsonb
);
```

---

## 11. Privacy & Compliance

* Hash or bucket sensitive IDs (`id`, `vat`, `license_plate`) in analytics.
* Keep plaintext only in raw event payloads with strict access control.
* Provenance fields (`event_id`, `rules_fired`, `confidence`) aid auditability.

---

## 12. Versioning & Idempotency

* Include `schema_version` in all files.
* De‑duplicate by `event_id` (UUID). Ignore duplicates on re‑ingest.

---

## 13. Quickstart

1. Start services: `docker compose up -d` (MinIO, FastAPI, Postgres, UI).
2. Run simulation: `POST /sim/run` with `smart_city_v1.yaml`.
3. Compute metrics: `POST /metrics/compute` for the desired window.
4. View results: open `VisualizationPage.vue` → select `pilot_tag = smart_city`.

---

## 14. Sample Data (3 Events)

```json
[
  {
    "schema_version":"1.0","event_id":"e1","application_id":"A-1","event_type":"ApplicationCreated",
    "occurred_at":"2025-11-10T09:00:00Z","actor":{"actor_id":"backend","actor_type":"system"},
    "source":"backend",
    "payload":{"applicant":{"name":"Eleni","surname":"Kosta","father":"Nikos"},"ids":{"id":"ID1","license_plate":"ZHX1234","vat":"EL123"},"address":"Athens","power_supply":"residential-single-phase","state":"pending","created_on":"2025-11-10T09:00:00Z"}
  },
  {
    "schema_version":"1.0","event_id":"e2","application_id":"A-1","event_type":"SystemScanCompleted",
    "occurred_at":"2025-11-10T09:01:10Z","actor":{"actor_id":"system-humai","actor_type":"system"},
    "source":"backend",
    "payload":{"system_processed_on":"2025-11-10T09:01:10Z","state_after":"needs_attention","system_findings":["vat"],"system_comments":"VAT format","confidence":0.76,"rules_fired":["R-101-vat-format"],"random_audit_flag":false}
  },
  {
    "schema_version":"1.0","event_id":"e3","application_id":"A-1","event_type":"OperatorReviewCompleted",
    "occurred_at":"2025-11-10T09:08:00Z","actor":{"actor_id":"1042","actor_type":"operator"},
    "source":"ui",
    "payload":{"operator_id":1042,"process_begins":"2025-11-10T09:05:20Z","duration_s":160,"state_after":"approved","operator_decision_code":"ACCEPT_FORMATTING_FIX","operator_reason_codes":["VAT_FORMAT"],"operator_comments":"Correct after re-entry","disagreement_with_system":false,"audit_type":"targeted"}
  }
]
```

---

## 15. Troubleshooting

* **Operator events rejected**: ensure current state is `needs_attention` or set `audit_type` to `escalation`.
* **Missing fairness slices**: check hashing/bucketing for IDs and that snapshot fields are present.
* **Low Tr metric**: inspect `disagreement_with_system` rates and `rules_fired` for noisy heuristics.

---

## 16. Checklist (Go‑Live)

* [ ] Enums wired into Operator UI (chips/selects)
* [ ] Pydantic models validated for 3 event types
* [ ] MinIO bucket policy and retention set
* [ ] Aggregator writes `aggregates/daily/*.json`
* [ ] Results registered with `pilot_tag = smart_city`
* [ ] Dashboards show F, D, HCL, Tr, EL + slices + finding quality
