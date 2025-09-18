
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

SCHEMA_VERSION = "1.0.0"

@dataclass
class Entity:
    entity_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Object(Entity):
    affordances: List[str] = field(default_factory=list)

@dataclass
class Agent(Entity):
    model: Optional[str] = None
    affordances: List[str] = field(default_factory=list)
    def act(self, action: str, obj: Object, effect: Optional[Dict[str, Any]] = None, t: Optional[int] = None):
        if action not in (set(self.affordances) | set(obj.affordances)):
            raise ValueError(f"Action '{action}' not allowed for {self.entity_id} on {obj.entity_id}")
        return Decision(SCHEMA_VERSION, "", t if t is not None else 0, self.entity_id, action, obj.entity_id, effect or {})

@dataclass
class Decision:
    schema_version: str
    sim_id: str
    t: int
    agent_id: str
    action: str
    object_id: str
    effect: Dict[str, Any] = field(default_factory=dict)
    correct: Optional[bool] = None
    latency_ms: Optional[int] = None
    def to_json(self) -> Dict[str, Any]:
        return asdict(self)

class Environment:
    def __init__(self, env_id: str, attributes: Optional[Dict[str, Any]] = None):
        self.env_id = env_id
        self.attributes = attributes or {}
        self.agents: Dict[str, Agent] = {}
        self.objects: Dict[str, Object] = {}
        self.sim_id: str = self.attributes.get("sim_id", "")
        self.logs: List[Decision] = []
    def add_agent(self, agent: Agent): self.agents[agent.entity_id] = agent
    def add_object(self, obj: Object): self.objects[obj.entity_id] = obj
    def record(self, decision: Decision):
        if not decision.sim_id: decision.sim_id = self.sim_id
        self.logs.append(decision)
    def to_log_json(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "env_id": self.env_id,
            "sim_id": self.sim_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "attributes": self.attributes,
            "agents": {k: {"attributes": v.attributes, "model": v.model, "affordances": v.affordances} for k,v in self.agents.items()},
            "objects": {k: {"attributes": v.attributes, "affordances": v.affordances} for k,v in self.objects.items()},
            "decisions": [d.to_json() for d in self.logs],
        }
