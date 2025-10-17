
# Simulator Workflow

Below is the sequence diagram of the simulation workflow:

![Simulator Workflow](simulator_workflow.svg "Simulator Workflow")

## Artifacts

- `haic_env_builder/configs/<Task>_env.yaml` — scenario description (task, agents, profiles)
- `metrics/<Task>_full_YYYY-MM-DD_HH-MM-SS.json` — simulation results (decisions, metrics, metadata)

## Config Shape (Universal Across Environments)

```yaml
task:
    name: CT Scan Diagnosis            # Task label
    parameters:
        environment: ct_scan            # Adapter selection
        env_params:                     # Passed only to the adapter
            steps: 12
            dt: 0.1
        # Optional, used by core:
        baseline_s:  null
        rt_max:      5.0

agents:
    - name: RadiologistAssistant
        modality: policy                # Optional at runtime; uses default if absent
    - name: VoiceSupportBot
        modality: policy

profiles:
    - profile_id: user123
        role: radiologist
        skill_level: expert
    - profile_id: user456
        role: technician
        skill_level: novice
```

## Notes

- Use `task.parameters.environment` to select an adapter (e.g., `ct_scan`, `overcooked`).
- Place environment-specific parameters under `task.parameters.env_params` so the core remains environment-agnostic.
- The legacy `adapter` field is still accepted, but `environment` is preferred.

### Core Guarantees

- **Environment-agnostic loop:** The runner only calls `adapter.reset()`, `adapter.action_space(name)`, and `adapter.step(action_map)`.
- **Canonical decisions:** Adapters emit rows with at least `{t, agent, action}`; if `t` is omitted, the core synthesizes it from `dt`.
- **Enrichment and metrics:** Applied uniformly across all environments (no hardcoded per-environment logic).

### Response Model (to API)

- `task`: str
- `agents`: list[str]
- `profiles`: list[str]
- `decisions`: list[dict]
- `metrics`: dict
- `info`: dict
- `status`: "success"
- `log_path`: str

## Adapter Contract

Each adapter must implement the following minimal and stable interface:

```python
def reset(seed: int | None) -> dict
def action_space(agent_name: str) -> Sequence[str]
def step(action_map: Dict[str, str]) -> tuple[StepOutput | dict, bool]
# StepOutput fields:
#   - decisions: list[dict]
#   - events: list[dict]
#   - info: dict
```

### Example Adapters

- **`ct_scan_adapter.py`** — Implements a toy workflow, echoing domain-specific verbs (e.g., `mark_finding`, `finalize_report`).
- **`overcooked_adapter.py`** — Bridges to a gridworld environment, using discrete actions: `"STAY"`, `"NORTH"`, `"SOUTH"`, `"WEST"`, `"EAST"`, `"INTERACT"`.

> **Note:** The Overcooked adapter is optional. If the required package is not installed, the adapter raises a clear `RuntimeError`.

