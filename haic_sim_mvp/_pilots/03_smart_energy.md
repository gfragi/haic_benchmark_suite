# Smart Energy — Simulation Spec (v0)

**Purpose** (what we compare):
Assess security-assessment policies (e.g., Baseline threshold vs Active-Learning aided vs Cost-aware deferral) on grid states produced by a Digital Twin, balancing accuracy, response time, and operator load/trust.

## Actors & Objects

- Agents

  - `Operator` - `OP` (`human`): view, inspect, accept/reject, annotate, approve action.
  - `ForecastAI` - `FA` (`ai`): day-ahead/short-term forecast, confidence.
  - `SecurityAI` - `SA` (`ai`): N-1 security classification (secure/insecure) with prob + XAI factors.

- Objects
  - `GridState` - `GS` (`object`): features (load, generation, topology), label (secure/insecure), ai_prob, xai_factors.
  - `DigitalTwin` - `DT` (`object`): simulate load flow, N-1 scenarios; returns grid state.

## HITL Workflow (minimal loop)

1. `ForecastAI.forecast(GridState)` → `prob_secure`, `xai_factors`.

2. **Policy routes**: if uncertain/high-risk → **defer to Operator**; else auto-classify.

3. `Operator.review` → **accept** or **override**; if override, add annotation (e.g., violated line, contingency).

4. Log decision + latencies; after N overrides or time T → **schedule retraining.**

## Policies to compare

- **Baseline** (Threshold): if `prob_secure ≥ τ` ⇒ AI decides; else defer.

- **AL-Aided**: prioritize AL-flagged grid states for human; auto on confident non-AL.

- **Cost-Aware** (optional): minimize expected cost combining error cost, human time, compute.

## Data Sources (dataset-driven mode)

- CSV rows = grid states with: `prob_secure`, `secure_gt` (ground truth), `al_flag`, `risk_score`, `region/site`, `weather_regime`, `ai_compute_ms`, `human_est_ms`, optional XAI fields.

## Metrics of interest

- **Base**: accuracy, defer_rate, avg_latency_ms.

- **HAIC Interaction metrics**: F, D, HCL, Tr, A, S, EL, EfficiencyScore.

- **Fairness**: slices by region, asset_type, weather_regime, time_of_day.

- **Trust/Usability**: SUS + trust item; Operator overrides as proxy for trust.

## Config Skeleton

```json
{
  "sim_id": "pilot_<name>_v0",
  "environment": {"id": "ENV", "class": "base.Environment",
    "attributes": {"task": "<task>", "domain": "<domain>"}},
  "agents": [
    {"id": "H", "class": "base.Agent", "model": "human", "affordances": ["view","classify","approve","reject"]},
    {"id": "AI", "class": "base.Agent", "model": "ai", "affordances": ["classify"]}
  ],
  "objects": [{"id": "X", "class": "base.Object", "affordances": ["view","classify","approve"]}],
  "script": []  // filled via dataset->script or scripted steps
}
```