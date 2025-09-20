# user_plugins/se_pilot.py
from dataclasses import dataclass
from haic_sim_mvp.engine.base import Agent, Object

@dataclass
class Operator(Agent):
    def act(self, action, obj, effect=None, t=None):
        if action == "accept" and not self.attributes.get("inspected"):
            raise ValueError("Inspect before accept")
        return super().act(action, obj, effect, t)

@dataclass
class DigitalTwin(Object):
    pass
