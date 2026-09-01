from pydantic import BaseModel, Field
from typing import Any, List, Optional


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
