from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime



class MetricGroupSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    metrics: Optional[List['MetricSchema']] = []

    class Config:
        from_attributes = True


class MetricSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    group_id: int

    class Config:
        from_attributes = True


class EvaluationResultMetricSchema(BaseModel):
    id: Optional[int]
    evaluation_result_id: int
    metric_id: int
    value: Optional[float]

    class Config:
        from_attributes = True


class EvaluationResultSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    configuration_id: int
    evaluation_date: Optional[datetime] = None
    metrics: List[EvaluationResultMetricSchema] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
