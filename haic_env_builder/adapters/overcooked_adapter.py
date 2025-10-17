# haic_env_builder/adapters/overcooked_adapter.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional

try:
    from .base import BaseAdapter
except Exception:
    class BaseAdapter:
        def reset(self, seed: Optional[int] = None): ...
        def step(self, action_map: Dict[str, str]): ...
        def action_space(self, agent_name: str) -> List[str]: ...
        def close(self): ...

# Discrete action set used by many Overcooked baselines
DISCRETE_ACTIONS = ["STAY", "NORTH", "SOUTH", "WEST", "EAST", "INTERACT"]

def _one_hot(actions: List[str], anchor: Optional[str]) -> Dict[str, float]:
    if not actions:
        return {}
    out = {a: 0.0 for a in actions}
    if anchor in out:
        out[anchor] = 1.0
    return out

def _bump_on(actions: List[str], anchor: Optional[str], p_anchor: float = 0.7) -> Dict[str, float]:
    if not actions:
        return {}
    n = len(actions)
    if anchor in actions and n > 1:
        rest = (1.0 - p_anchor) / (n - 1)
        return {a: (p_anchor if a == anchor else rest) for a in actions}
    # uniform fallback
    u = 1.0 / n
    return {a: u for a in actions}

class OvercookedAdapter(BaseAdapter):
    """
    Minimal, simulator-free Overcooked "progress" model.
    We approximate the onion soup workflow as a finite-state process:

      collect (need 3 onions) -> cook (start once pot has 3) -> wait (cook_ticks) -> serve (deliver) -> repeat

    For each step:
      - We mark an agent's action as `correct` if it advances the current phase (e.g., INTERACT during collect/serve,
        STAY during wait). Others are neutral/incorrect under this toy heuristic.
      - We emit `probs` (P_human) as a one-hot on the *expected* primitive for that phase.
      - We emit `surrogate_probs` (P_surrogate) as a soft bump around the executed action.
      - We also emit structured `events` describing progress.

    This keeps things self-contained and makes S/Tr/HCL meaningful immediately, without requiring overcooked_ai_py.
    """

    def __init__(self, **env_params: Any):
        p = dict(env_params or {})
        # knobs
        self.layout_name: str = p.get("layout_name", "cramped_room")
        self.target_deliveries: int = int(p.get("target_deliveries", 2))
        self.cook_ticks_required: int = int(p.get("cook_ticks_required", 15))  # ~ cooking time
        self.max_ticks: int = int(p.get("max_ticks", 360))                      # safety horizon

        # runtime state
        self.ticks: int = 0
        self.done: bool = False

        # soup state
        self.pot_onions: int = 0        # 0..3
        self.cooking: bool = False
        self.cook_ticks: int = 0
        self.ready: bool = False
        self.delivered: int = 0

    # --- adapter api ---
    def reset(self, seed: Optional[int] = None):
        self.ticks = 0
        self.done = False

        self.pot_onions = 0
        self.cooking = False
        self.cook_ticks = 0
        self.ready = False
        self.delivered = 0
        return {}

    def close(self):
        pass

    def action_space(self, agent_name: str) -> List[str]:
        return list(DISCRETE_ACTIONS)

    # --- phase helpers ---
    def _phase(self) -> str:
        if self.ready:
            return "serve"
        if self.cooking:
            return "wait"
        if self.pot_onions >= 3:
            return "cook"
        return "collect"

    def _expected_action(self) -> str:
        ph = self._phase()
        if ph in ("collect", "cook", "serve"):
            return "INTERACT"
        if ph == "wait":
            return "STAY"
        return "STAY"

    # --- state transitions & correctness ---
    def _apply_interact(self, events: List[Dict[str, Any]]) -> bool:
        """
        Apply an INTERACT effect according to current phase.
        Returns True if this INTERACT advanced the process (used as `correct` flag).
        """
        ph = self._phase()
        if ph == "collect" and self.pot_onions < 3:
            self.pot_onions += 1
            events.append({"event_type": "onion_added", "count": self.pot_onions})
            return True

        if ph == "cook" and not self.cooking:
            self.cooking = True
            self.cook_ticks = 0
            events.append({"event_type": "cooking_started"})
            return True

        if ph == "serve" and self.ready:
            self.ready = False
            self.pot_onions = 0
            self.cooking = False
            self.cook_ticks = 0
            self.delivered += 1
            events.append({"event_type": "soup_delivered", "delivered": self.delivered})
            return True

        # INTERACT during wait or when already cooking but not ready → no progress
        return False

    def _tick_cooking(self, events: List[Dict[str, Any]]):
        if not self.cooking or self.ready:
            return
        self.cook_ticks += 1
        events.append({"event_type": "cooking_tick", "tick": self.cook_ticks})
        if self.cook_ticks >= self.cook_ticks_required:
            self.ready = True
            events.append({"event_type": "soup_ready"})

    # --- main step ---
    def step(self, action_map: Dict[str, str]) -> Tuple[Dict[str, Any], bool]:
        if self.done:
            return {"decisions": [], "events": [], "info": self._info()}, True

        self.ticks += 1
        decisions: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []

        expected = self._expected_action()

        # 1) Apply simultaneous agent actions
        # To keep things simple: each INTERACT can advance at most once per tick (collect adds up to 3 though).
        # We'll process agents in deterministic name order for stability.
        for agent in sorted((action_map or {}).keys()):
            action = action_map[agent]
            space = self.action_space(agent)

            # correctness & transitions
            correct = False
            if action == "INTERACT":
                # collect/cook/serve advancement
                correct = self._apply_interact(events)
            elif action == "STAY":
                # only "wait" phase rewards STAY as correct
                correct = (self._phase() == "wait")

            # distributions
            probs = _one_hot(space, expected)                   # P_human: one-hot on expected primitive
            surrogate_probs = _bump_on(space, action, 0.7)      # P_surrogate: bump on executed action

            decisions.append({
                "agent": agent,
                "action": action,
                "correct": bool(correct),
                "probs": probs,
                "surrogate_probs": surrogate_probs,
            })

        # 2) Advance cooking timer after actions are applied
        self._tick_cooking(events)

        # 3) Stopping conditions
        if self.delivered >= self.target_deliveries:
            self.done = True
        if self.ticks >= self.max_ticks:
            self.done = True

        return {"decisions": decisions, "events": events, "info": self._info()}, self.done

    def _info(self) -> Dict[str, Any]:
        return {
            "layout": self.layout_name,
            "pot_onions": self.pot_onions,
            "cooking": self.cooking,
            "cook_ticks": self.cook_ticks,
            "ready": self.ready,
            "delivered": self.delivered,
            "target_deliveries": self.target_deliveries,
        }
