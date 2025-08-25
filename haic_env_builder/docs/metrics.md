# Metric Definitions

All simulations produce a metrics JSON (saved under `metrics/`) with:

```json
{
  "task": "...",
  "agents": ["..."],
  "profiles": ["..."],
  "metrics": {
    "steps": 5,
    "total_actions": 10,
    "collaboration_score": 0.87,
    "efficiency_score": 0.82
  },
  "decisions": [{"step":0,"agent":"...","action":"..."}],
  "status": "success",
  "log_path": "metrics/<file>.json"
}
```

## HAIC metric mapping (initial rules)

- Fidelity (F) – % of agent actions that align with task constraints.

- Diversity (D) – #unique action types / total actions.

- Human‑Centric Load (HCL) – proxy for steps requiring human oversight (can be inferred from profiles + action complexity).

- Trust (Tr) – heuristic from action consistency and error rate.

- Autonomy (A) – proportion of actions performed without human prompts.

- Safety (S) – #violations avoided / possible violations.

- Effort Load (EL) – estimated cognitive/interaction effort for humans (domain-specific model).

## File naming

`<TaskName>_metrics_YYYYMMDD_HHMMSS.json` (immutable per run)
