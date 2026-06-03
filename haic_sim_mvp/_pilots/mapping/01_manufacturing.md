
## Smart Manufacturing — Agents

| ID      | Role               | `model`  | `actor_type` in logs | Affordances                                    | What it represents             |
| ------- | ------------------ | -------- | -------------------- | ---------------------------------------------- | ------------------------------ |
| **SRL** | Scheduler RL       | `ai`     | `ai`                 | `propose_assignment`, `compute_confidence`     | Produces module/job proposals. |
| **PM**  | Production manager | `human`  | `human`              | `verify`, `approve`, `override`, `annotate`    | Reviews/decides assignments.   |
| **WC**  | Workcell / Module  | `system` | `system`             | `dispatch_job`, `process_start`, `process_end` | Executes production steps.     |
| **QC**  | Quality control    | `system` | `system`             | `label`, `record_outcome`                      | Emits outcome/ground truth.    |

## Smart Manufacturing — Objects

| ID      | Kind              | Affordances                     | What it represents        |
| ------- | ----------------- | ------------------------------- | ------------------------- |
| **Job** | `production_job`  | `assign`, `dispatch`, `process` | The production case/item. |
| **Mod** | `workcell_module` | `receive`, `execute`            | Target module/workcell.   |



## Action ↔ Log mapping (Manufacturing)

| Env `action`         | Log `action` / `event_type` | Typical payload keys                                                   |
| -------------------- | --------------------------- | ---------------------------------------------------------------------- |
| `propose_assignment` | `ai_proposal`               | `job_id`, `module_candidates[]`, `ai_prob`, `thresholds`, `latency_ms` |
| `verify` (PM)        | `pm_review`                 | `decision`, `selected_module`, `reason?`, `duration_s`                 |
| `dispatch_job`       | `dispatch_job`              | `job_id`, `module_id`                                                  |
| `process_start`      | `process_start`             | `module_id`                                                            |
| `process_end`        | `process_end`               | `proc_time_s`, `energy_wh`, `scrap`, `rework`                          |
| `label`              | `qc_label`                  | `meets_objective`, `defect_class?`, `correct`                          |
