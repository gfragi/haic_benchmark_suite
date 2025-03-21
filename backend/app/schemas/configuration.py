from datetime import datetime as dt
import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EvaluationConfigSchema(BaseModel):
    configuration_id: Optional[int] = Field(default=None, alias="id")
    application_name: str
    ai_model_name: str
    ai_model_type: str = Field(..., description="One of: Classification, Regression, Clustering, XAI, Swarm Learning, Active Learning, Other")
    metrics: list
    evaluation_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    description: Optional[str] = None
    config_type: str = Field(..., description="Either 'specific' or 'generic'")
    evaluation_status: str = Field(default="pending", description="Current status of the evaluation")


    class Config:
        from_attributes = True  # Allows from_orm to work with ORM models
        example = {
            "application_name": "My Application",
            "ai_model_name": "My AI Model",
            "ai_model_type": "Classification",
            "metrics": ["Effectiveness", "Efficiency"],
            "evaluation_date": "2025-03-21T10:00:00Z",
            "description": "Sample configuration.",
            "config_type": "specific",
            "evaluation_status": "pending"
            }