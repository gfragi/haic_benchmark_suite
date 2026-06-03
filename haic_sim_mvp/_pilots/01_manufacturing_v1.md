# Smart Manufacturing — Integration & Logging Spec_v1

**Scope**. Define the environment config, logging contract, and minimal adapters to integrate the real product-line workflow with the HAIC Benchmarking Platform. This updates the v0 spec to match the revised sequence (SchedulerRL → PM → Workcell/Module → QC/Label).

1) Environment Config (drop‑in JSON)

Use this as a reference or demo script. It matches your platform’s environment file schema.

```yaml
{
    "sim_id": "pilot_mfg_v0",
    "environment": {
        "id": "MFG_ENV",
        "class": "base.Environment",
        "attributes": { "task": "module_assignment", "domain": "manufacturing" }
    },
"agents": [
{ "id": "SRL", "class": "base.Agent", "model": "ai",
"affordances": ["propose_assignment","compute_confidence"] },
{ "id": "PM", "class": "base.Agent", "model": "human",
"affordances": ["verify","approve","override","annotate"] },
{ "id": "WC", "class": "base.Agent", "model": "system",
"affordances": ["dispatch_job","process_start","process_end"] },
{ "id": "QC", "class": "base.Agent", "model": "system",
"affordances": ["label","record_outcome"] }
],
"objects": [
{ "id": "Job", "class": "base.Object",
"attributes": {"kind":"production_job"},
"affordances": ["assign","dispatch","process"] },
{ "id": "Mod", "class": "base.Object",
"attributes": {"kind":"workcell_module"},
"affordances": ["receive","execute"] }
],
"script": [
{ "t": 0.0, "agent": "SRL", "action": "propose_assignment", "object": "Job",
"effect": {"job_id":"JB901","module_candidates":["W17","W21"],"ai_prob":0.62,
"thresholds":{"low":0.55,"high":0.8}},
"latency_ms": 95 },
{ "t": 1.3, "agent": "PM", "action": "verify", "object": "Job",
"effect": {"decision":"override","selected_module":"W21","reason":"tool wear alarm"},
"duration_s": 1.1 },
{ "t": 2.6, "agent": "WC", "action": "dispatch_job", "object": "Mod",
"effect": {"job_id":"JB901","module_id":"W21"} },
{ "t": 3.0, "agent": "WC", "action": "process_start", "object": "Mod",
"effect": {"module_id":"W21"} },
{ "t": 23.5, "agent": "WC", "action": "process_end", "object": "Mod",
"effect": {"proc_time_s":20.5,"energy_wh":112.0,"scrap":false,"rework":false} },
{ "t": 24.0, "agent": "QC", "action": "label", "object": "Job",
"effect": {"meets_objective":true,"defect_class":null}, "correct": true }
]
}
```

## Updated Event Map (from the new sequence diagram)

**Actors**: SchedulerRL (AI) → Production Manager (human) → Workcell/Module (system) → QC/Label (system/human). Log the following actions:

- **ai_proposal** — scheduler computes assignment; include `{job_id, module_candidates[], ai_prob, ai_compute_ms}`.

- **pm_review** — human verifies/inspects; include `duration_s` and `{decision: approve|override|request_info, selected_module?, reason?}`.

- **dispatch_job** — system dispatches job to module.

- **process_start / process_end** — execution; include `{proc_time_s, energy_wh, scrap, rework}` on end.

- **qc_label** — outcome label; set `correct` if it meets the objective.

**Group fields** (for fairness/efficiency slices): `line_id, workcell_id, shift, product_family, operator_bucket` (pseudonym).


Logging → Platform Session

**Session**: one production case or contiguous run (session_id).

**decisions[]** entries: each action above; fields: `t`, `actor_type`, `action`, `duration_s?|latency_ms`?, `payload{}`, optional correct.

**meta.task_parameters.rt_max:** set per station (e.g., 5s) for HCL proxy.

**Minimal CSV (dataset mode)**:

```bash
job_id,ai_prob,ground_truth,ai_latency_ms,human_latency_ms,module_id,vendor,shift,proc_time_s,energy_wh
J001,0.78,on_time,40,1200,M1,in_house,day,45,520
```

## Metrics (how your logs feed them)

- **F**: interactions per minute across the session window.

- **D**: average duration_s on human steps (PM).

- **HCL**: 1 − min(duration_s/rt_max, 1) for human steps.

- **Tr**: acceptance vs overrides and correctness at qc_label.

- **EL**: AI latency + cycle/cycle-time and energy.

- **Fairness**: parity across vendor/module/shift.


## Logging Contract (ENV - LOG map)

| Agent | Env affordance            | Log `action`              | actor_type | interaction_id           | object_id (optional) |
| ----- | ------------------------- | ------------------------- | ---------- | ------------------------ | -------------------- |
| SRL   | `ai_proposal`             | `ai_proposal`             | `ai`       | `job_id`                 | `Job`                |
| AH    | `propose_assignment`      | `propose_assignment`      | `system`   | `job_id`                 | `Mod`                |
| AH    | `dispatch_job`            | `dispatch_job`            | `system`   | `job_id`                 | `Mod`                |
| PM    | `change_objectives`       | `change_objectives`       | `human`    | `job_id` (if applicable) | `Obj`                |
| PM    | `bids_selected`           | `bids_selected`           | `human`    | `job_id` (if applicable) | `App`                |
| PM    | `phase_selected`          | `phase_selected`          | `human`    | `job_id` (if applicable) | `App`                |
| HMI   | `xr_panel_started`        | `xr_panel_started`        | `system`   | `job_id` (if applicable) | `App`                |
| HMI   | `xr_evaluation_completed` | `xr_evaluation_completed` | `system`   | `job_id` (if applicable) | `App`                |
| WC    | `process_start`           | `process_start`           | `system`   | `job_id`                 | `Mod`                |
| WC    | `process_end`             | `process_end`             | `system`   | `job_id`                 | `Mod`                |

### Timing fields

- Human steps (PM): add duration_s when you can (those contribute to D/HCL).

- AI/system steps (SRL, AH, WC, HMI): add latency_ms when you can (EL metric).

## Notes

- 'compute_confidence' → ai_proposal (aligns with the rest of Manufacturing).

- 'module_candidates' is now an array.

- 'duration' → 'duration_s'.

- Order is now: AI scores → HMI opens → PM chooses → AH dispatch → WC run → HMI completes.