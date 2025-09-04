# Pilot Integration Guide: Logging for the Benchmarking Suite

**Audience:** Teams (“pilots”) integrating real applications and exporting interaction logs for evaluation in the Benchmarking Suite.  
**Goal:** A shared, implementation-agnostic log format that works for both *simulations* and *real-world* runs.

---

## 1) What you log (at a glance)

You will export a **run log** consisting of:

- A **run header** (metadata about the app/run/config),
- A **sequence of decisions** (timestamped human/AI actions),
- Optional **environment events** (non-agent events),
- Optional **per-run artifacts** (custom info, notes).

The suite computes metrics (e.g., Accuracy, RT, Early/Late Accuracy, HCL, EL, EfficiencyScore, etc.) from these fields.  
If you follow this spec, your logs can be scored without code changes.

---

## 2) Required fields & units

### 2.1 Run header (top-level)

| Field | Type | Required | Notes |
|---|---|---:|---|
| `schema_version` | string | ✅ | Frozen interface version. Start with `"1.0"`. |
| `task` | string | ✅ | Scenario/Task name, e.g. `"CT Scan Review"`. |
| `app_id` | string | ✅ | Your application/system slug, e.g. `"acme_radassist"`. |
| `environment` | string | ✅ | Adapter/env name or `"real_world"`. |
| `rt_max` | number | ✅ | *Seconds.* Threshold for **early** vs **late** decisions and HCL scaling (e.g., `5.0`). |
| `baseline_s` | number\|null | ✅ | *Seconds.* Baseline total time used for **Effort Loss (EL)**. Use `null` if unknown. |
| `agents` | array | ✅ | List of agents; see schema below. |
| `seed` | integer\|null | — | If present, helps reproducibility. |
| `config_hash` | string | — | Stable hash to tie back to your config. |
| `info` | object | — | Free-form metadata (version, hardware, etc.). |

**Agent descriptor (each entry in `agents`):**

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | ✅ | Stable handle used in decisions, e.g. `"human1"`. |
| `name` | string | ✅ | Human-readable, e.g. `"Radiologist"` or `"AI Assistant"`. |
| `type` | `"human"`\|`"ai"` | ✅ | Agent archetype. |
| `action_space` | string[] | — | Enumerated valid actions for off-role detection (empty/omit if unknown). |

### 2.2 Decision record (each item in `decisions`)

| Field | Type | Required | Notes |
|---|---|---:|---|
| `t` | number | ✅ | *Seconds.* Monotonic timestamp from run start. If you only have wall-clock, normalize to seconds since start. |
| `agent` | string | ✅ | Must match one agent `id` from header. |
| `actor_type` | `"human"`\|`"ai"` | ✅ | Redundant with agent type—helps downstream logic. |
| `action` | string | ✅ | The labeled action name (free text or from action_space). |
| `duration_s` | number | — | *Seconds.* For human steps (typing, reading, etc.). |
| `latency_ms` | number | — | *Milliseconds.* For AI step latency (model response time, etc.). |
| `correct` | boolean\|null | — | Ground-truth correctness if known (`true`/`false`) else `null`. |
| `proposed_action` | string\|null | — | Optional policy-proposed action (before clamping). |
| `off_role_action` | boolean | — | If you can compute this; otherwise the suite will infer when `action_space` is supplied. |
| `event_type` | string | — | If this row is more like an event with an action (rare). |
| `meta` | object | — | Any extra per-decision data you want preserved. |

> **Units matter:**  
> - Use **seconds** for `t` and `duration_s`.  
> - Use **milliseconds** for `latency_ms`.  
> - Keep `t` **monotonic** (never decreasing).

### 2.3 Environment events (optional)

Non-agent events that should be on the run timeline but *aren’t* decisions:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `t` | number | ✅ | *Seconds.* |
| `type` | string | ✅ | Event category (e.g., `"alarm"`, `"system_state_change"`). |
| `data` | object | — | Free-form event payload. |

---

## 3) Early/Late & key metric prerequisites

The suite derives several metrics from the above fields. You **don’t** need to compute them yourself, but you **must** log the prerequisites:

- **Early vs Late**: A decision is **early** when `t <= rt_max`; otherwise **late**.
- **Accuracy (overall / early / late)**: Requires `correct` labels on decision rows where it makes sense (e.g., diagnostic choices).
- **Reaction Time (RT)**: Derived from `t` and the presence of decision types (first response, subsequent corrections).
- **Human-Centeredness Level (HCL)**: Uses `rt_max` partitioning of early vs late behavior; higher share of early, correct decisions generally improves HCL.
- **Effort Loss (EL) & EfficiencyScore**: Requires `baseline_s` and total run time.
- **Off-role**: Requires either your `off_role_action` flag or the `action_space` in the header to infer it.

> If a metric isn’t applicable for your app, you can still log decisions normally; the suite will compute whatever is meaningful from the available fields.

---

## 4) File formats

You can submit **JSON**, **JSONL**, or **CSV**. JSON is preferred for rich metadata.

### 4.1 JSON (single file)

```json
{
  "schema_version": "1.0",
  "task": "CT Scan Review",
  "app_id": "acme_radassist",
  "environment": "real_world",
  "rt_max": 5.0,
  "baseline_s": 120.0,
  "agents": [
    {"id": "human1", "name": "Radiologist", "type": "human", "action_space": ["look","decide","correct"]},
    {"id": "ai1", "name": "AI Assistant", "type": "ai", "action_space": ["suggest","explain"]}
  ],
  "seed": null,
  "info": {"app_version": "2.3.1"},
  "decisions": [
    {"t": 0.8, "agent": "human1", "actor_type": "human", "action": "look", "duration_s": 0.8, "correct": null},
    {"t": 1.0, "agent": "ai1", "actor_type": "ai", "action": "suggest", "latency_ms": 200, "correct": true},
    {"t": 3.1, "agent": "human1", "actor_type": "human", "action": "decide", "duration_s": 2.1, "correct": true}
  ],
  "events": [
    {"t": 2.5, "type": "system_state_change", "data": {"mode": "assist"}}
  ]
}
```

### 4.2 JSONL (line-delimited decisions)

Header block first, then one JSON per decision:

```
{"schema_version":"1.0","task":"CT Scan Review","app_id":"acme_radassist","environment":"real_world","rt_max":5.0,"baseline_s":120.0,"agents":[{"id":"human1","name":"Radiologist","type":"human"},{"id":"ai1","name":"AI Assistant","type":"ai"}]}
{"t":0.8,"agent":"human1","actor_type":"human","action":"look","duration_s":0.8}
{"t":1.0,"agent":"ai1","actor_type":"ai","action":"suggest","latency_ms":200,"correct":true}
{"t":3.1,"agent":"human1","actor_type":"human","action":"decide","duration_s":2.1,"correct":true}
```

> If you use JSONL, include a `header` object as the first line (as shown above) and optionally an `events` line later:
> `{"event":{"t":2.5,"type":"system_state_change","data":{"mode":"assist"}}}`

### 4.3 CSV (tabular)

Minimum viable columns (add more if you have them):

```
t,agent,actor_type,action,duration_s,latency_ms,correct
0.8,human1,human,look,0.8,, 
1.0,ai1,ai,suggest,,200,true
3.1,human1,human,decide,2.1,,true
```

Provide a small **sidecar** JSON file (same basename) for the header:

```json
{
  "schema_version": "1.0",
  "task": "CT Scan Review",
  "app_id": "acme_radassist",
  "environment": "real_world",
  "rt_max": 5.0,
  "baseline_s": 120.0,
  "agents": [
    {"id": "human1", "name": "Radiologist", "type": "human"},
    {"id": "ai1", "name": "AI Assistant", "type": "ai"}
  ]
}
```

---

## 5) Naming & packaging

- **File name:**  
  `<task>_<app_id>_<YYYYMMDD-HHMMSS>.<json|jsonl|csv>`  
  e.g., `ct_scan_review_acme_radassist_20250901-235900.json`
- **One run per file.** Zip multiple runs if needed.
- **Time zone:** Timestamps inside the log are **relative seconds**; no timezone concerns.

---

## 6) Validation

Before submission, validate:

- **Schema:** Required fields in header and decisions are present.  
- **Types/units:** Seconds vs milliseconds; booleans for `correct`.  
- **Monotonic `t`:** No time going backward.  
- **Agent IDs:** Every `decision.agent` exists in `agents`.  
- **Actor type match:** `actor_type` agrees with the referenced agent.

> If a field is unknown, use `null` (not empty strings) for numeric/boolean fields.

---

## 7) Submission / ingestion

Depending on your integration, you can:

- **File-drop**: provide the files via your agreed secure channel (e.g., S3 bucket, secure upload portal).  
- **API upload** *(if enabled in your deployment)*: POST the JSON file body to the ingestion endpoint you were given.  
- **Local evaluation**: place the file under the suite’s `metrics/` directory and run the evaluator CLI (dev/test flows).


---

## 8) Edge cases & tips

- **Multiple humans or AIs:** Add more `agents` entries; keep `agent` stable per person/bot.  
- **No correctness labels:** Set `correct: null`; metrics that rely on labels will be skipped or shown as N/A.  
- **Long-running apps:** Break logs into sessions; set `t=0` at each session start.  
- **Privacy:** Do **not** include PHI/PII in `meta` or `events`.  
- **Action taxonomy:** Keep action names consistent across runs; if your UI has free-text, consider mapping to a small controlled vocabulary before export.

---

## 9) FAQ

**Q: We only have wall-clock timestamps.**  
A: Convert to seconds since run start: `t = (ts_current - ts_start) / 1000.0`.

**Q: We can’t measure `duration_s` for humans reliably.**  
A: It’s optional. The suite will still compute many metrics from `t`, `action`, and `correct`.

**Q: How do we choose `rt_max`?**  
A: Use your domain’s typical “prompt reaction” boundary (e.g., 3–7s for visual inspection tasks). This drives early/late partitioning and HCL scaling.

**Q: How is Early/Late Accuracy defined?**  
A: By comparing each labeled decision’s `t` to `rt_max`: early if `t ≤ rt_max`, late otherwise.

---

## 10) Minimal working examples

### Minimal JSON (no labels, still valid)

```json
{
  "schema_version": "1.0",
  "task": "Triage",
  "app_id": "acme_triage",
  "environment": "real_world",
  "rt_max": 5.0,
  "baseline_s": null,
  "agents": [
    {"id":"human1","name":"Nurse","type":"human"},
    {"id":"ai1","name":"AI Triage","type":"ai"}
  ],
  "decisions": [
    {"t": 1.2, "agent":"human1","actor_type":"human","action":"open_case","duration_s":1.2},
    {"t": 2.0, "agent":"ai1","actor_type":"ai","action":"suggest","latency_ms":300}
  ]
}
```

### Rich JSON (with labels and action_space)

```json
{
  "schema_version": "1.0",
  "task": "CT Scan Review",
  "app_id": "acme_radassist",
  "environment": "real_world",
  "rt_max": 5.0,
  "baseline_s": 120.0,
  "agents": [
    {"id": "human1", "name": "Radiologist", "type": "human", "action_space": ["look","decide","correct"]},
    {"id": "ai1", "name": "AI Assistant", "type": "ai", "action_space": ["suggest","explain"]}
  ],
  "decisions": [
    {"t":0.8,"agent":"human1","actor_type":"human","action":"look","duration_s":0.8},
    {"t":1.0,"agent":"ai1","actor_type":"ai","action":"suggest","latency_ms":200,"correct":true},
    {"t":3.1,"agent":"human1","actor_type":"human","action":"decide","duration_s":2.1,"correct":true}
  ],
  "events": []
}
```

---

## 11) Versioning & change control

- Keep a `schema_version` field. If the suite evolves, we’ll publish `1.1`, `1.2`, etc.  
- New fields will be **additive** and **backward-compatible**.  
- Breaking changes will bump the **major** version.

---

## 12) Checklist before you ship

- [ ] `schema_version` present (e.g., `"1.0"`).  
- [ ] `task`, `app_id`, `environment`, `rt_max`, `baseline_s`, `agents` present.  
- [ ] Each decision has `t`, `agent`, `actor_type`, `action`.  
- [ ] Units: seconds for `t`/`duration_s`, milliseconds for `latency_ms`.  
- [ ] Agent IDs in decisions exist in header.  
- [ ] File name follows convention.  

---
