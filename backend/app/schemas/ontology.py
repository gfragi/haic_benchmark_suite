import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional

ENTITY_TYPES = (
    "domain", "action_type", "agent_role", "persona_archetype",
    "surrogate_tier", "metric_family", "template",
)
ENTITY_STATUSES = ("active", "draft", "deprecated")
_ENTITY_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class OntologyResponse(BaseModel):
    """Mirrors data/haic_ontology.json's top-level keys. Nested structures
    are left as Any deliberately - the ontology is a data file the
    frontend composer reads shape-first, not something we want to
    re-validate field-by-field in two places."""
    schema_: str = Field(..., alias="schema")
    version: str
    domains: List[Any]
    action_types: List[Any]
    agent_roles: List[Any]
    persona_archetypes: List[Any]
    surrogate_tiers: List[Any]
    metric_families: List[Any]
    templates: List[Any]

    class Config:
        populate_by_name = True


class SimulateProbabilisticRequest(BaseModel):
    name: str
    configuration_id: int = Field(..., description="Target configuration to ingest the generated sessions into")
    domain: str
    surrogate_tier: int = Field(..., ge=0, le=3)
    rt_max_s: float = 300.0
    baseline_s: Optional[float] = None
    n_items: int = 164
    n_sessions: int = 10
    persona: str = "aggregate"
    fitted_model: Optional[str] = None
    metrics: List[str] = ["Tr", "HCL", "EL", "F", "S"]
    pilot_tag: str = "surrogate_probabilistic"
    app_version: str = "sim_v2.0.0"
    ai_model_version: str = "markov-1.0"
    seed: int = 42


class SimulateProbabilisticResponse(BaseModel):
    status: str
    n_sessions_generated: int
    n_decisions_total: int
    surrogate_tier: int
    persona: str
    run_ids: List[str]
    pilot_tag: str
    warnings: List[str] = []


class OntologyEntityIn(BaseModel):
    entity_id: str
    label: str
    description: Optional[str] = None
    properties: Dict[str, Any]
    status: str = "active"

    @field_validator("entity_id")
    @classmethod
    def _valid_entity_id(cls, v: str) -> str:
        if not _ENTITY_ID_RE.match(v):
            raise ValueError("entity_id must match ^[a-z][a-z0-9_]*$")
        return v

    @field_validator("properties")
    @classmethod
    def _non_empty_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("properties must be a non-empty dict")
        return v

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if v not in ENTITY_STATUSES:
            raise ValueError(f"status must be one of {ENTITY_STATUSES}")
        return v


class OntologyEntityUpdate(BaseModel):
    label: str
    description: Optional[str] = None
    properties: Dict[str, Any]
    status: str = "active"

    @field_validator("properties")
    @classmethod
    def _non_empty_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("properties must be a non-empty dict")
        return v

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if v not in ENTITY_STATUSES:
            raise ValueError(f"status must be one of {ENTITY_STATUSES}")
        return v


class OntologyEntityOut(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    status: str
    properties: Dict[str, Any]
    version: int


class OntologyDeleteResponse(BaseModel):
    message: str
    entity_id: str


class OntologyUsageResponse(BaseModel):
    entity_type: str
    entity_id: str
    usage_count: int
    recent_scenarios: List[str]
