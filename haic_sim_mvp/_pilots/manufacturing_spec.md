# Smart Manufacturing — Simulation Spec (v0)

**Purpose** (what we compare):
Benchmark Human–AI scheduling for the DFKI SmartFactory “Production Island _KUBA” with a reproducible simulation + metrics workflow.
We compare policies (heuristics, RL, RL+deferral) on identical data and quantify technical and human-in-the-loop (HAIC) outcomes.

- **Scheduling policy quality**: Baseline heuristic vs ABOS-RL (or RL proxy) vs RL + Human-in-the-Loop deferral (L2D-like).

- **Trade-offs**: accuracy (meets objective) vs latency and human load (defer rate).

- **Operator impact**: trust/overrides, cognitive load proxy (HCL), adaptability during the session.

- **(Optional) Fairness / equity**: outcomes per module/vendor/shift.

## Actors & Objects

- `Agents
`
  - `Operator` - `OP` (`human`): can `set_goal`, `approve`, `override`.
  - `SchedulerRL` - `SRL` (`ai`): bid, assign, emits confidence (eg. softmax(Q)).
  - `Machine_i` - `M1...Mk` (`surrogate/ai`): process → `{done/energy/time}`.
  - `QualityControl` - `QC` (`ai/human`): inspect.

- Objects
  - `Job` - `JB`: `order/task` unit with `steps`, `due_date`, `priority`, `status`.
  - `Workcell/Module` - `W*`*: resource that executes a job step.
  - `DigitalTwin` (`DT`, optional object): provides labels/metrics for outcomes.

- Affordances (examples)

  - `SRL`: assign
  - `OP`: approve, override, set_goal
  - `Machine`: process
  - `QC`: inspect

## HITL Workflow (minimal loop)

[![HITL workflow](../figures/BS_diagrams-smart_energy.png)](../figures/BS_diagrams-smart_energy.png)

## Policies to compare

1.** BaselineThreshold(τ₀)**

    - If `ai_prob ≥ τ₀` → **AI assigns**, else **Human decides**.

    - Single knob: `threshold ∈ [0,1]`.

2. **L2D-like(τ)** (uncertainty deferral)

    - If `ai_prob ∈ (1−τ, τ)` → defer to **Human**; else **AI acts**.

    - Knob: `τ ∈ [0.5, 0.99]` (larger → wider deferral band).

3. **(Optional) CostAware(α, β)**
    - Predict composite utility `U = α·on_time_prob − β·energy_norm`, **defer** if |U| < ε (uncertain), else act by sign(U).

## Data Sources (dataset-driven mode)

### Minimal CSV (works with your A/B tab mapper):

```bash
job_id, ai_prob, ground_truth, ai_latency_ms, human_latency_ms, module_id, vendor, shift, proc_time_s, energy_wh
J001,   0.78,    on_time,      40,            1200,             M1,       in_house, day, 45,         520
J002,   0.41,    late,         35,            1400,             M2,       external, night, 60,       740
...
```

- **Required**: `ai_prob` (0..1), `ground_truth` (e.g., `on_time`/`late` or `secure`/`insecure`), `job_id`.
- **Optional**: `ai_latency_ms`, `human_latency_ms`, `module_id/vendor/shift` (for fairness), `proc_time_s`, `energy_wh`.

### Dataset→Script mapping (engine does this):

- Each row → one **case** (object = `Job_i`).

- Policy decides who acts; we log:
  - `effect` (e.g., `{assign_to:"M2", ai_prob:0.78}`) on AI step.
  - correct on final step if it **matches ground_truth** (meets objective).

## Metrics of interest

### Technical (from `engine.evaluate`)

- accuracy (meets objective fraction)
- ai_accuracy / human_accuracy
- defer_rate
- avg_latency_ms (mix of AI/Human steps)

### HAIC interaction metrics

- F (interactions/min), D (mean action duration), HCL (1 − RT/RTmax)
- Tr (1 − errors/N_labeled), A (late−early accuracy, tanh-clamped), S (surrogate similarity)
- EL + EfficiencyScore (effort loss vs baseline)

### Fairness (optional, easy to add)

- Outcome parity (accuracy) by `vendor/module/shift`
- Override asymmetry (human override rate) by group
- Load equity (task share, wait times) by group

## Config Skeleton (scripted demo)

```json
{
  "sim_id": "kuba_demo",
  "environment": {
    "id": "KUBA",
    "class": "base.Environment",
    "attributes": { "task": "scheduling", "domain": "manufacturing" }
  },
  "agents": [
    { "id": "OP",  "class": "base.Agent", "model": "human", "affordances": ["set_goal","approve","override"] },
    { "id": "SRL", "class": "base.Agent", "model": "ai",     "affordances": ["assign"] }
  ],
  "objects": [
    { "id": "J1", "class": "base.Object", "affordances": ["assign","process"], "attributes": {"type":"job"} },
    { "id": "M1", "class": "base.Object", "affordances": ["process"], "attributes": {"type":"module"} }
  ],
  "script": [
    { "t": 1, "agent": "SRL", "action": "assign", "object": "J1",
      "latency_ms": 40, "effect": {"assign_to":"M1","ai_prob":0.78} },
    { "t": 2, "agent": "OP", "action": "approve", "object": "J1",
      "latency_ms": 1200, "correct": true }
  ]
}
```

### (Optional) Plugin scaffold `user_plugins/manufacturing.py`

```python

from dataclasses import dataclass
from typing import Optional, Dict, Any
from haic_sim_mvp.engine.base import Agent, Object

@dataclass
class Operator(Agent):
    def act(self, action: str, obj: Object,
            effect: Optional[Dict[str, Any]] = None, t: Optional[int] = None):
        # Example policy gate: require 'assign' exists before 'approve'
        if action in {"approve","override"} and not effect and not obj.attributes.get("assigned"):
            raise ValueError("No assignment to approve/override")
        return super().act(action, obj, effect, t)

@dataclass
class Workcell(Object):
    pass
```

- Register in `haic_sim_mvp/engine/__init__.py`:
`user_plugins.kuba.Operator`, `user_plugins.kuba.Workcell`.

## Acceptance checks (v0)

- A/B completes on a 50–200 row CSV with mapped columns; logs appear in `results/`.
- Metrics render without KeyErrors; Comparison suggests a winner.
- Changing τ increases defer_rate and (usually) accuracy up to a point.
- Optional fairness slices show differences by `vendor/module` if provided.

