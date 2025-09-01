# backend/app/schemas/collab.py
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Decision(BaseModel):
    t: float = Field(..., description="Event timestamp (sec, monotonic within a session)")
    agent: Optional[str] = Field(None, description="Agent/human identifier")
    actor_type: Optional[str] = Field(None, description="'human' | 'ai' (optional, used by HCL, per-agent)")
    action: Optional[str] = Field(None, description="Free-text action label")
    duration_s: Optional[float] = Field(None, ge=0, description="Action duration (sec)")
    latency_ms: Optional[float] = Field(None, ge=0, description="Alternative latency (ms), used if duration_s missing")
    correct: Optional[bool] = Field(None, description="Outcome flag for Tr/A")
    probs: Optional[Dict[str, float]] = Field(None, description="Human (or primary) class prob. dist.")
    surrogate_probs: Optional[Dict[str, float]] = Field(None, description="Surrogate model prob. dist.")
    surrogate_action: Optional[str] = Field(None, description="Fallback if probs are missing")
    event_type: Optional[str] = Field(None, description="Optional: 'error' marks an error event")

class ComputeRequest(BaseModel):
    decisions: List[Decision]
    rt_max: float = Field(5.0, gt=0, description="Upper cap for reaction-time scaling in HCL (sec)")
    baseline_s: Optional[float] = Field(None, gt=0, description="Baseline for EL (efficiency/latency)")

class MetricsOut(BaseModel):
    F: float
    D: float
    HCL: float
    Tr: float
    A: float
    S: float
    EL: float

class PerAgentMetrics(BaseModel):
    agent: str
    metrics: MetricsOut

class CollabMetricsResponse(BaseModel):
    version: str = "2.1.0"
    metrics_version: str = "collab-0.2.0"
    source: str
    params: Dict[str, Optional[float]]
    metrics: MetricsOut
    by_agent: List[PerAgentMetrics] = []
