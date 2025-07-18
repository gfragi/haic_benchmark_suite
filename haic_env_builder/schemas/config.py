from pydantic import BaseModel
from typing import List, Literal, Dict

class TaskSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, str]

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
