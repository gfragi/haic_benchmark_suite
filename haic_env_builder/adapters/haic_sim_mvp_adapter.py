from typing import Dict, Any, List, Optional, Tuple
import json
import copy

from haic_env_builder.adapters.base import EnvAdapter, StepOutput

class HAICSimMVPAdapter(EnvAdapter):
    """
    Adapter for haic_sim_mvp style JSON configurations.
    Handles scripted simulations with agents, objects, and policies.
    """

    name = "haic_sim_mvp"

    def __init__(self, env_params: Optional[Dict[str, Any]] = None, **kwargs: Any):
        if env_params is None and isinstance(kwargs.get("env_params"), dict):
            env_params = kwargs["env_params"]

        env_params = dict(env_params or {})
        self.config: Dict[str, Any] = env_params.get("config", {})

        # Extract entities from config
        self.environment = self.config.get("environment", {})
        self.agents = {a["id"]: a for a in self.config.get("agents", [])}
        self.objects = {o["id"]: o for o in self.config.get("objects", [])}
        self.script = self.config.get("script", [])

        self.current_step = 0
        self.t = 0.0
        self._done = False

        # Initialize agents' viewed_cases if needed
        for agent in self.agents.values():
            if "attributes" not in agent:
                agent["attributes"] = {}
            if "viewed_cases" not in agent["attributes"]:
                agent["attributes"]["viewed_cases"] = []

    def configure(self, env_params: Optional[Dict[str, Any]] = None):
        if env_params is not None:
            self.config = env_params.get("config", {})
            self.environment = self.config.get("environment", {})
            self.agents = {a["id"]: a for a in self.config.get("agents", [])}
            self.objects = {o["id"]: o for o in self.config.get("objects", [])}
            self.script = self.config.get("script", [])

            # Re-initialize agents' viewed_cases
            for agent in self.agents.values():
                if "attributes" not in agent:
                    agent["attributes"] = {}
                if "viewed_cases" not in agent["attributes"]:
                    agent["attributes"]["viewed_cases"] = []

        self.current_step = 0
        self.t = 0.0
        self._done = False
        return self

    def action_space(self, agent_id: str) -> List[str]:
        if agent_id in self.agents:
            return self.agents[agent_id].get("affordances", [])
        return []

    def reset(self, seed: Optional[int] = None):
        self.current_step = 0
        self.t = 0.0
        self._done = False

        # Reset agent states
        for agent in self.agents.values():
            if "attributes" not in agent:
                agent["attributes"] = {}
            agent["attributes"]["viewed_cases"] = []

        return {}

    def close(self):
        pass

    def _normalize_step(self, s: dict) -> dict:
        s = dict(s or {})
        # common aliases
        if "obj" in s and "object" not in s:
            s["object"] = s.pop("obj")
        # types
        if "t" in s:
            try: s["t"] = int(s["t"])
            except: pass
        if "latency_ms" in s and s["latency_ms"] is not None:
            try: s["latency_ms"] = int(s["latency_ms"])
            except: pass
        if "correct" in s and isinstance(s["correct"], str):
            s["correct"] = s["correct"].lower() in {"1","true","yes","y"}
        return s

    def step(self, action_map: Dict[str, str]) -> Tuple[StepOutput, bool]:
        if self._done or self.current_step >= len(self.script):
            self._done = True
            return StepOutput(decisions=[], events=[], info={}), True

        step_config = self._normalize_step(self.script[self.current_step])
        self.current_step += 1

        agent_id = step_config.get("agent", "")
        action = step_config.get("action", "")
        object_id = step_config.get("object", "")
        effect = step_config.get("effect", {})
        correct = step_config.get("correct")
        latency_ms = step_config.get("latency_ms")

        # Update agent state (e.g., viewing)
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if action == "view" and object_id not in agent["attributes"]["viewed_cases"]:
                agent["attributes"]["viewed_cases"].append(object_id)

        # Validate affordances
        agent_affordances = set(self.agents.get(agent_id, {}).get("affordances", []))
        object_affordances = set(self.objects.get(object_id, {}).get("affordances", []))
        allowed_actions = agent_affordances | object_affordances

        if action not in allowed_actions:
            # For now, just log the violation but continue
            print(f"Warning: Action '{action}' not allowed for agent '{agent_id}' on object '{object_id}'")

        # Determine actor type
        agent_model = self.agents.get(agent_id, {}).get("model", "human")
        actor_type = "ai" if agent_model == "ai" else "human"

        # Update time
        if isinstance(latency_ms, (int, float)):
            self.t += float(latency_ms) / 1000.0  # Convert ms to seconds

        decision = {
            "t": self.t,
            "agent": agent_id,
            "actor_type": actor_type,
            "action": action,
            "object": object_id,
            "correct": correct if isinstance(correct, bool) else None,
        }

        if effect:
            decision["effect"] = effect
        if isinstance(latency_ms, (int, float)):
            decision["latency_ms"] = float(latency_ms)

        return StepOutput(decisions=[decision], events=[], info={}), (self.current_step >= len(self.script))
