
from dataclasses import dataclass
from typing import Optional, Dict, Any
from haic_mvp_sim.engine.base import Agent, Object

@dataclass
class Radiologist(Agent):
    def act(self, action: str, obj: Object, effect: Optional[Dict[str, Any]] = None, t: Optional[int] = None):
        viewed = self.attributes.setdefault("viewed_cases", [])
        if action == "classify" and obj.entity_id not in viewed:
            raise ValueError("Radiologist must 'view' before 'classify'")
        return super().act(action, obj, effect, t)

@dataclass
class CTImage(Object):
    pass
