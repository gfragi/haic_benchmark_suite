from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict

class MetricSchema(BaseModel):
    metric_name: str

class EvaluationConfigSchema(BaseModel):
    config_id: Optional[int] = Field(None, alias="id")
    application_name: str
    ai_model_name: str
    metrics: List[MetricSchema]
    evaluation_date: Optional[str] = None
    description: Optional[str] = None
    config_type: str  # Either 'specific' or 'generic'

    class Config:
        json_schema_extra = {
            "example": {
                "application_name": "RadiologyApp",
                "ai_model_name": "TumorDetectionModelV1",
                "metrics": [
                    {"metric_name": "Prediction Accuracy"},
                    {"metric_name": "Response Time"},
                ],
                "evaluation_date": "2024-07-01",
                "description": "Evaluation of Tumor Detection Model in RadiologyApp",
                "config_type": "specific",
                "application_specific_details": {
                    "specific_field_radiology_1": "Example detail specific to Radiology",
                    "specific_field_radiology_2": "Another example"
                },
            }
        }