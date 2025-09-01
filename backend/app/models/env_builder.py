from pydantic import BaseModel
from typing import List, Optional, Literal
import re

class AgentIn(BaseModel):
    id: str
    type: Literal["human", "ai"]
    profile: Optional[str] = "default"

class MetricsIn(BaseModel):
    rt_max: float = 5.0
    baseline_s: Optional[float] = None

class ActionIn(BaseModel):
    id: str
    name: str
    actor: str
    duration_s: Optional[float] = None
    latency_ms: Optional[float] = None
    correct: Optional[bool] = None

class TaskIn(BaseModel):
    id: str
    name: str
    actions: List[ActionIn] = []

class EnvBuilderIn(BaseModel):
    name: str
    version: str
    metrics: MetricsIn
    agents: List[AgentIn]
    tasks: List[TaskIn] = []
    environment: Optional[str] = None  # optional env selector

class GenerateRequest(BaseModel):
    task_name: str
    env: EnvBuilderIn

def _slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")