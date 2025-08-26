from pydantic import BaseModel, field_validator
from typing import List, Literal, Dict, Any

def _coerce_scalar(v: Any) -> Any:
    if isinstance(v, str):
        s = v.strip()
        low = s.lower()
        if low in {"true", "false"}:
            return low == "true"
        # try int/float
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            return v
    return v

class TaskSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

    @field_validator("parameters", mode="before")
    @classmethod
    def coerce_params(cls, v):
        if isinstance(v, dict):
            return {k: _coerce_scalar(val) for k, val in v.items()}
        return v

class AgentSchema(BaseModel):
    name: str
    capabilities: List[str]
    modality: Literal['text', 'audio', 'visual']

class ProfileSchema(BaseModel):
    id: str
    skill_level: Literal['novice', 'intermediate', 'expert']
    role: str

class ConfigSchema(BaseModel):
    task: TaskSchema
    agents: List[AgentSchema]
    profiles: List[ProfileSchema]
