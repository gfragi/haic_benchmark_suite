# Adding a New Scenario

## 1) Author a YAML config
Create `haic_env_builder/configs/My_Scenario_env.yaml`:
```yaml
task:
  name: "Kitchen Toy Task"
  description: "Assemble a soup under constraints."
  parameters:
    layout: "cramped"
    max_steps: 50

agents:
  - name: "CookBot"
    capabilities: ["pickup","drop","pot"]
    modality: "discrete"

profiles:
  - id: "userA"
    skill_level: "intermediate"
    role: "operator"
```

## 2) (Optional) Add domain logic

If your scenario needs richer behavior, implement it under:

- `haic_env_builder/scenarios/<domain>.py`
- haic_env_builder/components/*.py (Agent, Task, Profile already exist)

The simulator loads YAML → `Task`, `Agent`, `Profile` objects and loops for N steps calling `Agent.act(task)`. Extend `Agent.act` (or provide a domain agent class) to add meaningful actions.

