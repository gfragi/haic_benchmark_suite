from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class MessageWithPath(BaseModel):
    message: str
    path: str

class ConfigList(BaseModel):
    available_configs: List[str]

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

class ErrorEnvelope(BaseModel):
    error: ErrorDetail

class SimulationResult(BaseModel):
    task: str
    agents: List[str]
    profiles: List[str]
    metrics: Dict[str, float]
    decisions: List[Dict[str, Any]]
    status: str
    seed: Optional[int] = None
    config_hash: Optional[str] = None
    log_path: Optional[str] = None

class SimulationEnvelope(BaseModel):
    simulation_result: SimulationResult

class MetricsList(BaseModel):
    files: List[str]

class MetricsEnvelope(BaseModel):
    metrics: Dict[str, Any]

class MetricsLoadResponse(BaseModel):
    metrics: Dict[str, float] = Field(..., description="Computed metrics (F, D, HCL, Tr, A, S, EL)")
    artifact: Dict[str, Any] = Field(..., description="Full artifact JSON for inspection")