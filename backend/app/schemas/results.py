from pydantic import BaseModel, Field
from typing import Dict, Optional

class EvaluationResultSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    log_id: int
    metrics: Dict[str, float]
    evaluation_date: Optional[str] = None

    class Config:
        from_attributes = True

class EvaluationResultQuerySchema(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    ai_model_name: Optional[str] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None

    class Config:
        from_attributes = True