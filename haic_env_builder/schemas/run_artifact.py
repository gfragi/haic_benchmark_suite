from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from datetime import datetime

class Decision(BaseModel):
    t: float = Field(..., ge=0)
    agent: str
    actor_type: Literal["human", "ai"]
    action: str
    latency_ms: Optional[float] = Field(None, ge=0)
    duration_s: Optional[float] = Field(None, ge=0)
    correct: Optional[bool] = True
    probs: Optional[Dict[str, float]] = None

class Metrics(BaseModel):
    F: float
    D: float
    HCL: float
    Tr: float
    A: float
    S: float
    EL: float

class RunArtifact(BaseModel):
    version: str = Field("sim-0.1.0", pattern=r"^sim-\d+\.\d+\.\d+$")
    task: str
    seed: Optional[int] = None
    config_hash: Optional[str] = None
    T: Optional[float] = Field(None, ge=0)
    baseline_s: Optional[float] = Field(None, ge=0)
    agents: Optional[List[str]] = None
    profiles: Optional[List[str]] = None
    decisions: List[Decision] = Field(..., min_length=1) # at least one decision
    metrics: Metrics
    status: Literal["success", "failed"] = "success"
    written_at: datetime = Field(default_factory=datetime.utcnow)

    
