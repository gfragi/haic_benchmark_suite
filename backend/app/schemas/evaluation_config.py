from pydantic import BaseModel, Field
from typing import List, Optional

class MetricSchema(BaseModel):
    metric_name: str
    metric_formula: Optional[str] = None
    description: Optional[str] = None

class EvaluationConfigSchema(BaseModel):
    config_id: Optional[int] = Field(None, alias="id")  
    application_name: str
    ai_model_name: str
    metrics: List[MetricSchema]
    evaluation_date: Optional[str] = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "application_name": "RadiologyApp",
                "ai_model_name": "TumorDetectionModelV1",
                "metrics": [
                    {"metric_name": "Prediction Accuracy", "metric_formula": "TP + TN / Total Predictions", "description": "Accuracy of predictions"},
                    {"metric_name": "Response Time", "metric_formula": "Total Response Time / Number of Queries", "description": "Average time per query"},
                    # Add more metrics as needed
                ],
                "evaluation_date": "2024-07-01",
                "description": "Evaluation of Tumor Detection Model in RadiologyApp"
            }
        }
