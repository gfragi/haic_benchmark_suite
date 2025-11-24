# SmartGrid-HAIC Benchmark (Agentbeats Scenario)

This folder defines the **SmartGrid-HAIC** scenario for Agentbeats, implemented as a **green agent** (assessor) plus a baseline **purple agent** (operations agent).

The goal is to evaluate how an operations agent manages a simplified smart-grid environment and how well it collaborates with a (simulated) human/operator, using the existing HAIC simulation and metrics stack.

---

## Files

- `smartgrid_assessor.py`  
  Green Agent (assessor) for the SmartGrid-HAIC benchmark.  
  - Creates a `haic_sim_mvp.engine.base.Environment` and initializes a toy smart-grid state (`grid_state`) with:
    - `step`, `max_steps`
    - `load_level` (`high` / `medium` / `low`)
    - `alert` (boolean)
    - `blackout` (boolean)
    - `incidents_avoided`, `penalty_cost`
  - Runs an interaction loop:
    1. Builds an observation (`_build_state`) and sends it to the operations agent via A2A.
    2. Receives an `action` from the operations agent.
    3. Applies the action with `_apply_action_and_get_effect`, updating `grid_state` and creating a `Decision` recorded in the `Environment`.
  - At the end of the episode:
    - Exports a log with `env.to_log_json()`.
    - Computes **task metrics** via `evaluate.basic_metrics(log)`.
    - Computes **HAIC collaboration metrics** via `metrics_bridge.haic_metrics_for_log(log)`.
    - Combines them into a single `overall_score` and returns an `AssessmentResult` with:
      - `metrics["score"] = overall_score`
      - a JSON artifact containing per-episode and aggregate metrics.

- `ops_agent.py`  
  Purple Agent (baseline operations agent).  
  - Receives `TaskUpdate` messages with `payload["state"]` from the green agent.
  - Uses a simple rule-based policy (`choose_action`) based on:
    - `alert` flag
    - `load_level`
  - Returns `payload["action"]` with one of:
    - `"shed_load"` (e.g. when there is a high-load alert),
    - `"inspect"`,
    - `"do_nothing"`.
  - This serves as a baseline agent; it can later be replaced or extended by LLM-based or more advanced policies.

- `smartgrid_common.py`  
  Placeholder for future helpers (e.g. wrapping a future `SmartGridCoreEnv` or custom metric utilities).  
  Currently not required for the first running prototype.

- `scenario.toml`  
  Agentbeats scenario configuration.  
  - Declares:
    - The SmartGridAssessor as the **green agent**.
    - The OpsAgent as a **participant** with role `"ops"`.
  - Provides assessment parameters (e.g. `num_episodes`, `difficulty`, `max_steps`).

---

## How It Works (High Level)

1. `agentbeats-run` reads `scenario.toml` and starts:
   - the **green agent** (`smartgrid_assessor.py`),
   - the **purple agent** (`ops_agent.py`).

2. The green agent:
   - Initializes the HAIC `Environment` and `grid_state`.
   - For each timestep:
     - Serializes the current state (`_build_state`) and sends it to the OpsAgent.
     - Receives an action from the OpsAgent.
     - Applies the action to update the smart-grid state (`_apply_action_and_get_effect`), creating a `Decision` and recording it in the log.

3. At the end of the episode:
   - The log is exported via `env.to_log_json()`.
   - Task-level and HAIC collaboration metrics are computed.
   - A final score and full metric breakdown are returned as an `AssessmentResult`.

This setup reuses the existing **HAIC simulation** (`haic_sim_mvp`) and **metrics** (`metrics_bridge`, `metrics_core`), and simply adds an Agentbeats-compatible evaluation harness around them.

---

## Running the Scenario

From the project root (where `pyproject.toml` and `src/agentbeats` live), run:

```bash
uv run agentbeats-run scenarios/smartGrid/scenario.toml --show-logs
