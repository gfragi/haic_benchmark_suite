# haic_env_builder/adapters/base.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Sequence, Tuple, Optional

@dataclass
class StepOutput:
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)

class EnvAdapter:
    name: str = "generic"
    version: str = "1.0.0"

    def reset(self, *, seed: Optional[int] = None) -> Dict[str, Any]:
        return {"env": self.name, "version": self.version}

    def action_space(self, agent_name: str) -> Sequence[str]:
        return ()

    def step(self, action_map: Dict[str, str]) -> Tuple[StepOutput, bool]:
        raise NotImplementedError

    def close(self) -> None:
        pass
