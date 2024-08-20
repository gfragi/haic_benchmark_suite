from pydantic import BaseModel, Field
from typing import Dict, Optional

class EvaluationResultSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    log_id: int
    metrics: Dict[str, float]
    evaluation_date: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "log_id": 1,
                "metrics": {
                    "Prediction Accuracy": 0.95,
                    "Response Time": 0.5
                },
                "evaluation_date": "2024-06-28T12:30:00Z"
            }
        }

class EvaluationResultQuerySchema(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    ai_model_name: Optional[str] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "ai_model_name": "TumorDetectionModelV1",
                "min_accuracy": 0.9,
                "max_accuracy": 1.0
            }
        }