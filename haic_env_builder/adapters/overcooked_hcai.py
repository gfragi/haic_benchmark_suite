from typing import Any, Dict, Optional, Tuple, List
import time
import random

from .base import EnvAdapter

# HC-AI overcooked imports (names are indicative; adjust if needed)
from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld
from overcooked_ai_py.agents.agent import AgentEvaluator

# Minimal action space (adjust to full set as you expand)
DISCRETE_ACTIONS = ["NORTH", "SOUTH", "EAST", "WEST", "STAY", "INTERACT"]

class OvercookedHCAdapter(EnvAdapter):
    """
    Wraps HumanCompatibleAI/overcooked_ai to your Decision schema.
    """

    def __init__(self, layout_name: str, horizon_s: int = 120, **kwargs):
        self.layout_name = layout_name
        self.horizon_s = horizon_s
        self._ae = None
        self._t0 = None
        self._t = 0.0

        # Configure evaluator (state featurizer + env)
        # AgentEvaluator usually wants mdp + horizon; follow their examples
        mdp = OvercookedGridworld.from_layout_name(self.layout_name)
        self._ae = AgentEvaluator.from_layout_name(self.layout_name, **kwargs)
        self._mdp = mdp
        self._ep_done = False

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            random.seed(seed)
        self._t0 = time.time()
        self._t = 0.0
        self._ep_done = False
        # The evaluator often has rollout helpers; but we keep it manual here.
        # Return an initial "observation" dict (you can expand this)
        return {"obs": "start", "t": self._t}

    def _now_t(self) -> float:
        return time.time() - self._t0 if self._t0 else 0.0

    def step(self, actions: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
        """
        actions = {"agent_0": "NORTH", "agent_1": "INTERACT"} (strings)
        Convert to Overcooked action indices and advance.
        """
        if self._ep_done:
            return {"decisions": []}, True, {"reason": "episode_already_done"}

        # Map to env actions (HC-AI expects ints; adjust if needed)
        a0 = DISCRETE_ACTIONS.index(actions.get("agent_0", "STAY"))
        a1 = DISCRETE_ACTIONS.index(actions.get("agent_1", "STAY"))

        # Step the environment; use AgentEvaluator rollout API or env directly.
        # Below we simulate a step result; replace with real env stepping.
        # For actual HC-AI usage you'd do something like:
        # next_state, reward, done, info = env.step((a0, a1))
        # Here we'll just fake a reward/done for wiring.
        reward = 0.0
        done = False
        info = {"deliveries": 0, "shaped_reward": reward}

        # Build decision logs for each agent
        ts = self._now_t()
        decisions = []
        for agent_id, act_str in actions.items():
            decisions.append({
                "t": ts,
                "agent": agent_id,
                "actor_type": "ai",        # or "human" if mapped
                "action": act_str,
                "latency_ms": 50.0,        # set real latency if you measure it
                "duration_s": 0.2,         # time to perform action if available
                "correct": None,           # set via env info if you define correctness
                "probs": None,
            })

        self._t = ts
        self._ep_done = done or (self._t >= self.horizon_s)
        return {"decisions": decisions}, self._ep_done, info

    def close(self): ...
