# haic_env_builder/adapters/overcooked_adapter.py
from __future__ import annotations
from typing import Dict, Any, Sequence, Tuple, Optional, List
from dataclasses import dataclass
from .base import EnvAdapter, StepOutput

# Default Overcooked discrete actions
_DEFAULT_ACTIONS: Tuple[str, ...] = ("STAY","NORTH","SOUTH","WEST","EAST","INTERACT")

# --- Try to import the real env; otherwise we'll still expose a working adapter ---
_HAS_OVERCOOKED = True
try:
    # Minimal import surface; you can expand if you wire true dynamics
    from overcooked_ai_py.mdp.overcooked_env import OvercookedEnv  # type: ignore
    from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld  # type: ignore
except Exception:
    _HAS_OVERCOOKED = False


@dataclass
class MissingDependencyAdapter(EnvAdapter):
    """Smoke adapter that emits a single dependency_missing event and completes."""
    name: str = "overcooked"
    version: str = "0.0.0-missing"
    missing: str = "overcooked_ai_py"

    def __init__(self, **_):
        self._done = False
        self.dt = float(_ .get("dt", 0.1)) if isinstance(_, dict) else 0.1
        self._t = 0.0
        self._k = 0

    def reset(self, *, seed: Optional[int] = None) -> Dict[str, Any]:
        self._done = False
        self._t = 0.0
        self._k = 0
        return {"env": self.name, "version": self.version, "dt": self.dt, "seed": seed, "missing": self.missing}

    def action_space(self, agent_name: str) -> Sequence[str]:
        return _DEFAULT_ACTIONS

    def step(self, action_map: Dict[str, str]) -> Tuple[StepOutput, bool]:
        # One informative event, then we're done
        events = [{
            "t": self._t,
            "event_type": "dependency_missing",
            "package": self.missing,
            "message": f"Install '{self.missing}' to enable Overcooked simulation."
        }]
        info = {"tick": self._k, "dt": self.dt, "env": self.name, "missing": self.missing}
        self._t += self.dt
        self._k += 1
        done = True
        return StepOutput(decisions=[], events=events, info=info), done

    def close(self) -> None:
        pass


@dataclass
class OvercookedAdapter(EnvAdapter):
    """
    Lightweight wrapper; if the real env is available, you can plug it here.
    For now, we provide a horizon-based mock that echoes actions with stable timing.
    """
    name: str = "overcooked"
    version: str = "1.0.0"

    # Mock params (work both with and without the true env wired)
    layout_name: str = "cramped_room"
    horizon_s: float = 30.0
    dt: float = 0.1

    def __init__(self, layout_name: str = "cramped_room", horizon_s: float = 30.0, dt: float = 0.1, **_):
        self.layout_name = layout_name
        self.horizon_s = float(horizon_s)
        self.dt = float(dt)
        self._t = 0.0
        self._k = 0
        self._horizon_ticks = max(1, int(self.horizon_s / max(1e-9, self.dt)))

        # If you hook the real env later, initialize it here under an `if _HAS_OVERCOOKED:` guard.

    def reset(self, *, seed: Optional[int] = None) -> Dict[str, Any]:
        self._t = 0.0
        self._k = 0
        # Initialize real env under _HAS_OVERCOOKED if desired
        return {"env": self.name, "version": self.version, "layout": self.layout_name, "dt": self.dt, "seed": seed}

    def action_space(self, agent_name: str) -> Sequence[str]:
        return _DEFAULT_ACTIONS

    def step(self, action_map: Dict[str, str]) -> Tuple[StepOutput, bool]:
        decisions: List[Dict[str, Any]] = []

        # In a true integration, you'd pass actions to the env and extract state/reward.
        # We keep a minimal echo for now.
        for name, act in action_map.items():
            act_final = act if act in _DEFAULT_ACTIONS else "STAY"
            decisions.append({
                "t": self._t,
                "agent": name,
                "action": act_final,
                "duration_s": 0.0,
            })

        events: List[Dict[str, Any]] = []
        info = {"tick": self._k, "dt": self.dt, "env": self.name, "layout": self.layout_name}

        self._t += self.dt
        self._k += 1
        done = (self._k >= self._horizon_ticks)

        return StepOutput(decisions=decisions, events=events, info=info), done

    def close(self) -> None:
        pass
