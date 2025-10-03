
from dataclasses import dataclass
from typing import Optional, Dict, Any
from haic_sim_mvp.engine.base import Agent, Object

@dataclass
class Radiologist(Agent):
    def act(self, action: str, obj: Object,
            effect: Optional[Dict[str, Any]] = None, t: Optional[int] = None):
        # ensure a list to track viewed case IDs
        viewed = self.attributes.setdefault("viewed_cases", [])

        # record the view
        if action == "view":
            if obj.entity_id not in viewed:
                viewed.append(obj.entity_id)

        # enforce the gating rule
        if action == "classify" and obj.entity_id not in viewed:
            raise ValueError("Radiologist must 'view' before 'classify'")

        return super().act(action, obj, effect, t)

@dataclass
class CTImage(Object):
    pass
