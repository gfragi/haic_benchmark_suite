from datetime import datetime as dt
import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EvaluationConfigSchema(BaseModel):
    config_id: Optional[int] = Field(default=None, alias="id")
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

        json_schema_extra = {
            "example": {
                "application_name": "RadiologyApp",
                "ai_model_name": "TumorDetectionModelV1",
                "ai_model_type": "Classification",
                "metrics": [
                    {"metric_name": "Prediction Accuracy"},
                    {"metric_name": "Response Time"},
                ],
                "evaluation_date": dt.utcnow().isoformat(),
                "description": "Evaluation of Tumor Detection Model in RadiologyApp",
                "config_type": "specific",
                "evaluation_status": "pending"
            }
        }