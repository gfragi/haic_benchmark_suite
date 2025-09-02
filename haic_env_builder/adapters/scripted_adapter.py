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
    name = "scripted"

    def __init__(self, env_params: Optional[Dict[str, Any]] = None, **kwargs: Any):
        if env_params is None and isinstance(kwargs.get("env_params"), dict):
            env_params = kwargs["env_params"]

        env_params = dict(env_params or {})
        if isinstance(kwargs.get("script"), dict):
            env_params["script"] = kwargs["script"]
        if "tasks" in kwargs and isinstance(kwargs["tasks"], list):
            env_params["script"] = {"tasks": kwargs["tasks"]}

        self.env_params: Dict[str, Any] = env_params
        self.script: Dict[str, Any] = (self.env_params.get("script") or {})

        self.plan: List[Dict[str, Any]] = []
        for t in (self.script.get("tasks") or []):
            for a in (t.get("actions") or []):
                self.plan.append(dict(a))

        self.i = 0
        self.t = 0.0
        self._done = False

    def configure(self, env_params: Optional[Dict[str, Any]] = None):
        if env_params is not None:
            self.env_params = dict(env_params)
        self.script = (self.env_params.get("script") or {})
        self.plan = []
        for t in (self.script.get("tasks") or []):
            for a in (t.get("actions") or []):
                self.plan.append(dict(a))
        self.i = 0
        self.t = 0.0
        self._done = False
        return self

    def action_space(self, agent_id: str) -> List[str]:
        tasks = (self.script or {}).get("tasks", []) or []
        names: List[str] = []
        if tasks:
            for t in tasks:
                for a in (t.get("actions") or []):
                    if a.get("actor") == agent_id and a.get("name"):
                        names.append(a["name"])
        else:
            for a in self.plan:
                if a.get("actor") == agent_id and a.get("name"):
                    names.append(a["name"])
        return list(dict.fromkeys(names))

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

        agent   = str(row.get("actor") or "")
        name    = str(row.get("name") or "")
        dur_s   = row.get("duration_s", None)
        lat_ms  = row.get("latency_ms", None)
        correct = row.get("correct", None)

        actor_type = "ai" if lat_ms is not None and dur_s in (None, "", 0) else "human"
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

        return {"decisions": [decision]}, (self.i >= len(self.plan))
