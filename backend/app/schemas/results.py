from pydantic import BaseModel, Field
from typing import Optional

class EvaluationResultSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    log_id: int
    prediction_accuracy: Optional[float] = None
    response_time: Optional[float] = None
    teaching_efficiency: Optional[float] = None
    overall_system_accuracy: Optional[float] = None
    objective_fulfillment_rate: Optional[float] = None
    feedback_impact: Optional[float] = None
    adaptability_score: Optional[float] = None
    query_efficiency: Optional[float] = None
    error_reduction_rate: Optional[float] = None
    confidence: Optional[float] = None
    model_improvement_rate: Optional[float] = None
    resource_utilization: Optional[float] = None
    impact_of_corrections: Optional[float] = None
    decision_effectiveness: Optional[float] = None
    knowledge_retention: Optional[float] = None
    task_completion_time: Optional[float] = None
    trust_score: Optional[float] = None
    safety_incidents: Optional[float] = None
    adversarial_robustness: Optional[float] = None
    domain_generalization: Optional[float] = None
    system_reliability: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    human_ai_agreement_rate: Optional[float] = None
    time_to_resolution: Optional[float] = None
    human_effort_saved: Optional[float] = None
    ai_assistance_rate: Optional[float] = None
    learning_efficiency: Optional[float] = None
    correction_efficiency: Optional[float] = None
    evaluation_date: Optional[str] = None



    class Config:
        from_attributes = True