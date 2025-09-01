from typing import Dict, Any, List, Optional, Tuple

try:
    from .base import BaseAdapter
except Exception:
    class BaseAdapter:
        def reset(self, seed: Optional[int] = None): ...
        def step(self, action_map: Dict[str, str]): ...
        def action_space(self, agent_name: str) -> List[str]: ...
        def close(self): ...

class ScriptedAdapter(BaseAdapter):
    """
    Very simple interpreter for UI-built scripts.
    It flattens env_params['script']['tasks'][*]['actions'] and emits one decision per step.
    - Human actions: use duration_s (seconds)
    - AI actions:    use latency_ms (ms)
    - 'correct' may be true/false/None
    """
    name = "scripted"

    def __init__(self, **env_params: Any):
        script = (env_params or {}).get("script", {}) or {}
        tasks = script.get("tasks") or []
        self.plan: List[Dict[str, Any]] = []
        for t in tasks:
            for a in (t.get("actions") or []):
                self.plan.append(dict(a))
        self.i = 0
        self.t = 0.0
        self._done = False

    def reset(self, seed: Optional[int] = None):
        self.i = 0
        self.t = 0.0
        self._done = False
        return {}

    def close(self): ...

    def step(self, action_map: Dict[str, str]) -> Tuple[Dict[str, Any], bool]:
        if self._done or self.i >= len(self.plan):
            self._done = True
            return {"decisions": [], "events": [], "info": {}}, True

        row = self.plan[self.i]
        self.i += 1

        # build a single decision
        agent = str(row.get("actor") or "")
        name  = str(row.get("name")  or "")
        dur_s = row.get("duration_s", None)
        lat_ms = row.get("latency_ms", None)
        correct = row.get("correct", None)

        # crude actor_type inference
        actor_type = "ai" if lat_ms is not None and dur_s in (None, "", 0) else "human"

        # advance time if we have a duration
        if isinstance(dur_s, (int, float)) and dur_s > 0:
            self.t += float(dur_s)

        decision = {
            "t": self.t,
            "agent": agent,
            "actor_type": actor_type,
            "action": name,
            "correct": correct if isinstance(correct, bool) else None,
        }
        if isinstance(dur_s, (int, float)):
            decision["duration_s"] = float(dur_s)
        if isinstance(lat_ms, (int, float)):
            decision["latency_ms"] = float(lat_ms)

        return {"decisions": [decision], "events": [], "info": {}}, (self.i >= len(self.plan))
