# schemas/decision.py
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Literal, Optional
from datetime import datetime

SCHEMA_VERSION = "1.0.0"

ActionLevel = Literal["low", "high"]
EventType = Literal[
    "tick", "move", "interact", "pickup", "drop", "handoff",
    "collision", "idle", "task_progress", "reward", "done",
]

class PolicyInfo(BaseModel):
    model_id: Optional[str] = None
    logprob: Optional[float] = None
    value: Optional[float] = None
    temperature: Optional[float] = None

class Decision(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_version: str = Field(default=SCHEMA_VERSION)
    sim_id: str
    t: int
    agent_id: str
    action: str
    level: ActionLevel = "low"
    rationale: Optional[str] = None
    policy: Optional[PolicyInfo] = None
    observation_hash: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def make(sim_id: str, t: int, agent_id: str, action: str, **kw) -> "Decision":
        return Decision(sim_id=sim_id, t=t, agent_id=agent_id, action=action, **kw)

class StateSnapshot(BaseModel):
    t: int
    env: str
    state_repr: Dict[str, Any] = {}
    obs: Dict[str, Any] = {}
    rng_state: Optional[str] = None

    @staticmethod
    def from_overcooked(env, state, t: int) -> "StateSnapshot":
        # Minimal, stable representation
        return StateSnapshot(
            t=t, env="overcooked_hcai",
            state_repr={
                "pot_states": getattr(state, "pot_states", None),
                "onions_in_soup": getattr(state, "objects_in_pots", None),
            },
            obs={},  # fill if you have per-agent obs
        )

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_version: str = Field(default=SCHEMA_VERSION)
    sim_id: str
    t: int
    type: EventType
    payload: Dict[str, Any] = {}
    reward_delta: float = 0.0

    @staticmethod
    def tick(sim_id: str, t: int, env: str, reward_delta: float = 0.0) -> "Event":
        return Event(sim_id=sim_id, t=t, type="tick", payload={"env": env}, reward_delta=reward_delta)

class StepInfo(BaseModel):
    t: int
    state: StateSnapshot
    info: Dict[str, Any] = {}

    @staticmethod
    def state_factory(env: str, t: int) -> "StepInfo":
        return StepInfo(t=t, state=StateSnapshot(t=t, env=env), info={})
