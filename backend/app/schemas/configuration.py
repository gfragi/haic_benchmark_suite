from datetime import datetime as dt
import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationConfigSchema(BaseModel):
    configuration_id: Optional[int] = Field(default=None, alias="id")
    application_name: str
    ai_model_name: str
    ai_model_type: str = Field(..., description="One of: Classification, Regression, Clustering, XAI, Swarm Learning, Active Learning, Other")
    metrics: List = Field(default_factory=list)
    pilot_tag: Optional[str] = None
    baseline_s: Optional[float] = None
    evaluation_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    description: Optional[str] = None
    config_type: str = Field(..., description="Either 'specific' or 'generic'")
    evaluation_status: str = Field(default="pending", description="Current status of the evaluation")

    class Config:
        from_attributes = True
        populate_by_name = True