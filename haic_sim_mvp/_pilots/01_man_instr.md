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