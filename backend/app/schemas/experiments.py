from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

MODEL_ROLES = ("source", "target")


class ExperimentRunIn(BaseModel):
    name: str
    description: Optional[str] = None
    domain: str
    source_model_id: str
    n_sessions: int = 20
    n_items: int = 164
    smooth_epsilon: float = 0.005


class ExperimentModelIn(BaseModel):
    model_id: str
    model_label: Optional[str] = None
    role: str
    log_file_path: Optional[str] = None
    fitted_model_path: Optional[str] = None

    @field_validator("role")
    @classmethod
    def _valid_role(cls, v: str) -> str:
        if v not in MODEL_ROLES:
            raise ValueError(f"role must be one of {MODEL_ROLES}")
        return v

    class Config:
        # model_id/model_label collide with Pydantic v2's reserved "model_"
        # attribute prefix (model_dump(), model_validate(), etc.) - this is
        # just a naming collision warning, not an actual conflict, since
        # these are real domain fields (an AI model's id/label).
        protected_namespaces = ()


class ExperimentModelOut(BaseModel):
    id: UUID
    experiment_id: UUID
    model_id: str
    model_label: Optional[str] = None
    role: str
    domain: str
    log_file_path: Optional[str] = None
    fitted_model_path: Optional[str] = None
    ai_action_frequency: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        protected_namespaces = ()


class ExperimentResultOut(BaseModel):
    id: UUID
    experiment_id: UUID
    model_a_id: str
    model_b_id: str
    comparison_type: str

    pred_Tr: Optional[float] = None
    pred_Tr_std: Optional[float] = None
    pred_HCL: Optional[float] = None
    pred_HCL_std: Optional[float] = None
    pred_EL: Optional[float] = None
    pred_EL_std: Optional[float] = None
    pred_F: Optional[float] = None
    pred_F_std: Optional[float] = None

    real_Tr: Optional[float] = None
    real_HCL: Optional[float] = None
    real_EL: Optional[float] = None
    real_F: Optional[float] = None

    err_Tr_pct: Optional[float] = None
    err_HCL_pct: Optional[float] = None
    err_EL_pct: Optional[float] = None
    err_F_pct: Optional[float] = None

    S_cross: Optional[float] = None
    S_cross_per_action: Optional[Dict[str, Any]] = None

    h1_supported: Optional[bool] = None
    h2_supported: Optional[bool] = None
    h3_supported: Optional[bool] = None

    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        protected_namespaces = ()


class ExperimentRunOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    domain: str
    source_model_id: str
    n_sessions: int
    n_items: int
    smooth_epsilon: float
    status: str
    created_at: datetime
    sealed_at: Optional[datetime] = None
    revealed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        protected_namespaces = ()


class ExperimentSummary(ExperimentRunOut):
    model_count: int


class ExperimentDetail(ExperimentRunOut):
    models: List[ExperimentModelOut] = []
    results: List[ExperimentResultOut] = []


class ExperimentCreateResponse(BaseModel):
    experiment_id: UUID
    status: str


class ExtractRequest(BaseModel):
    model_id: str

    class Config:
        protected_namespaces = ()


class PredictRequest(BaseModel):
    target_model_id: Optional[str] = None


class RevealRequest(BaseModel):
    model_id: Optional[str] = None

    class Config:
        protected_namespaces = ()


class CompareRequest(BaseModel):
    model_a_id: Optional[str] = None
    model_b_id: Optional[str] = None

    class Config:
        protected_namespaces = ()


class ExperimentDeleteResponse(BaseModel):
    message: str
    experiment_id: UUID
