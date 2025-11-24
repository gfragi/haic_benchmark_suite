# Green Agent 

from typing import Dict, Any, List, Tuple
import random


from src.green_executor import GreenExecutor
from src.models import AssessmentRequest, AssessmentResult, TaskUpdate, Artifact

from haic_sim_mvp.engine.base import Environment, Agent, Object, Decision
from haic_sim_mvp.engine.metrics_bridge import haic_metrics_for_log
from haic_sim_mvp.engine.evaluate import compute_metrics as basic_metrics


class SmartGridAssessor(GreenExecutor):

    async def run_assessment(self, request: AssessmentRequest) -> AssessmentResult:
        cfg = request.config.params or {}
        num_episodes = cfg.get("num_episodes", 1)

        ops_participant = request.participants_by_role["ops"]
        ops_endpoint = ops_participant.endpoint

        episode_results: List[Dict[str, Any]] = []

        for ep in range(num_episodes):
            episode_results.append(
                await self._run_single_episode(ops_endpoint, cfg, ep)
            )

        # aggregate (mean score)
        avg_score = sum(ep["overall_score"] for ep in episode_results) / max(len(episode_results), 1)

        artifact = Artifact(
            type="application/json",
            name="smartgrid_haic_results.json",
            content={
                "episodes": episode_results,
                "aggregate": {
                    "overall_score": avg_score,
                },
            },
        )

        return AssessmentResult(
            metrics={"score": avg_score},
            artifacts=[artifact],
        )

    async def _run_single_episode(self, ops_endpoint: str, cfg: Dict[str, Any], ep_idx: int) -> Dict[str, Any]:
        # Environment
        env = Environment(env_id=f"smartgrid_env_ep{ep_idx}", attributes={
            "scenario": "smartgrid",
            "difficulty": cfg.get("difficulty", "medium"),
        })
        # Initial grid state
        env.attributes["grid_state"] = {
            "step": 0,
            "max_steps": cfg.get("max_steps", 5), # max timesteps in episode
            "load_level": "high",       # start with high load
            "alert": True,              # there is initially an alert
            "region": "R1",
            "blackout": False,
            "incidents_avoided": 0,
            "penalty_cost": 0.0,
        }

        # agents (also i can get from 03_energy_env.json)
        env.add_agent(Agent(entity_id="OPS", model="ai", affordances=["act"], attributes={}))
        env.add_agent(Agent(entity_id="HUM", model="human", affordances=["act"], attributes={}))

        # objects = π.χ. lines, substations, incidents
        # env.add_object(...)

        t = 0
        done = False

        while not done:
            t += 1

            state_dict = self._build_state(env, t) # helpers for state building

            # send state to OpsAgent
            update = TaskUpdate(
                message=f"[t={t}] SmartGrid state",
                payload={"state": state_dict, "timestep": t},
            )
            response = await self.send_message(endpoint=ops_endpoint, update=update)
            action = response.payload["action"]  # e.g. {"type": "shed_load", "region": "R1"}

            # simulate the effect of the action (your own logic)
            effect, done, correct, latency_ms = self._apply_action_and_get_effect(env, state_dict, action)

            # build Decision with your own schema
            decision = env.agents["OPS"].act(
                action="act",
                obj=Object(entity_id="GRID", attributes={}, affordances=["act"]),
                effect=effect,
                t=t,
            )
            decision.correct = correct
            decision.latency_ms = latency_ms
            env.record(decision)

            await self._emit_update(f"[t={t}] action={action} effect={effect}")

        # Τέλος episode → metrics
        log = env.to_log_json()

        task_m = basic_metrics(log)
        haic_m = haic_metrics_for_log(log)

        # Συνδυασμός σε overall_score
        task_score = task_m.get("accuracy", 0.0) or 0.0
        collab_score = haic_m.get("normalized_collab_score", 0.0) if haic_m else 0.0
        overall = 0.5 * task_score + 0.5 * collab_score

        return {
            "episode_index": ep_idx,
            "task_metrics": task_m,
            "haic_metrics": haic_m,
            "overall_score": overall,
        }

    async def _emit_update(self, msg: str):
        await self.send_task_update(TaskUpdate(message=msg, payload={}))

    def _build_state(self, env: Environment, t: int) -> Dict[str, Any]:
        grid_state = env.attributes.get("grid_state", {})
        # Update step
        grid_state["step"] = t
        env.attributes["grid_state"] = grid_state

        # Raw info
        raw = {
            "step": grid_state.get("step"),
            "max_steps": grid_state.get("max_steps"),
            "load_level": grid_state.get("load_level"),
            "alert": grid_state.get("alert"),
            "region": grid_state.get("region"),
            "blackout": grid_state.get("blackout"),
            "incidents_avoided": grid_state.get("incidents_avoided"),
            "penalty_cost": grid_state.get("penalty_cost"),
        }

        # Natural language summary (optional, but helpful)
        summary = (
            f"Step {raw['step']} of {raw['max_steps']}. "
            f"Region {raw['region']} has load level {raw['load_level']}. "
            f"Current alert status: {'ACTIVE' if raw['alert'] else 'no active alerts'}. "
            f"Blackout: {'YES' if raw['blackout'] else 'no'} so far. "
            f"Incidents avoided: {raw['incidents_avoided']}, penalty cost: {raw['penalty_cost']}."
        )

        return {
            "raw": raw,
            "summary": summary,
            "recommended_actions_hint": [
                "If there is an active alert and load is high, consider shedding load.",
                "Avoid unnecessary shedding when there is no alert, to minimize penalty cost.",
            ],
        }

    def _apply_action_and_get_effect(
        self,
        env: Environment,
        state: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], bool, bool, int]:
        """
        Returns: effect_dict, done, correct, latency_ms
        """
        grid_state = env.attributes.get("grid_state", {}).copy()
        raw = state.get("raw", {})
        step = raw.get("step", grid_state.get("step", 0))
        max_steps = raw.get("max_steps", grid_state.get("max_steps", 5))

        act_type = action.get("type", "do_nothing")

        alert = bool(raw.get("alert", False))
        blackout = bool(raw.get("blackout", False))
        penalty_cost = float(raw.get("penalty_cost", 0.0))
        incidents_avoided = int(raw.get("incidents_avoided", 0))

        events = []

        # Simple latency model (μπορείς να το συνδέσεις αργότερα με πραγματικό χρόνο)
        latency_ms = action.get("latency_ms", 200)

        if alert and act_type == "shed_load":
            # Resolve the alert successfully
            alert = False
            incidents_avoided += 1
            events.append("alert_resolved")
            # lower the load level one notch
            load_level = raw.get("load_level", "high")
            if load_level == "high":
                load_level = "medium"
            elif load_level == "medium":
                load_level = "low"
            else:
                load_level = "low"
            correct = True

        elif alert and act_type == "do_nothing":
            # Risk of blackout
            if random.random() < 0.5:
                blackout = True
                penalty_cost += 100.0
                events.append("blackout_occurred")
                correct = False
            else:
                events.append("near_miss_no_blackout")
                correct = False
            load_level = raw.get("load_level", "high")

        elif not alert and act_type == "shed_load":
            # unnecessary shedding
            penalty_cost += 10.0
            events.append("unnecessary_shedding")
            load_level = raw.get("load_level", "medium")
            correct = False

        else:
            # inspect or do_nothing without alert
            events.append("no_critical_event")
            load_level = raw.get("load_level", "medium")
            correct = not alert  # correct if no alert and no action

        # update step
        step += 1

        # update grid_state
        grid_state.update(
            {
                "step": step,
                "max_steps": max_steps,
                "load_level": load_level,
                "alert": alert,
                "blackout": blackout,
                "incidents_avoided": incidents_avoided,
                "penalty_cost": penalty_cost,
            }
        )
        env.attributes["grid_state"] = grid_state

        # termination condition
        done = blackout or (step >= max_steps)

        effect = {
            "event_type": events[-1] if events else "none",
            "events": events,
            "new_state": grid_state,
        }

        return effect, done, correct, latency_ms
