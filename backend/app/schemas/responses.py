from pydantic import BaseModel
from typing import Any


class HealthResponse(BaseModel):
    status: str                  # "ok" | "degraded"
    uptime_s: float
    version: str
    db_ok: bool
    minio_ok: bool


class EvaluationStartedResponse(BaseModel):
    detail: str
    message: str                 # backward compat
    status: str                  # "running"
    log_count: int
    configuration_id: int


class LogIngestResponse(BaseModel):
    detail: str
    configuration_id: int
    log_id: int
    minio_path: str
    event_count: int             # number of decisions in the registered log
    validation_warnings: list[str]   # from MetricResult.warning fields
    derived: dict[str, Any] = {}


class UploadResponse(BaseModel):
    detail: str
    minio_paths: list[str]


class MetricWarning(BaseModel):
    metric: str
    warning: str


class EvaluationResultResponse(BaseModel):
    configuration_id: int
    status: str
    metrics: dict[str, float | None]     # value or None
    warnings: list[MetricWarning] = []   # surfaces MetricResult.warning
    artifact_path: str | None = None
