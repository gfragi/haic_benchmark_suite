from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict, Union


class SystemMetrics(BaseModel):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


class ValidationData(BaseModel):
    ai_detection_results: Optional[str] = None
    confidence_scores: Optional[Dict[str, float]] = None
    validation_results: Optional[str] = None
    confidence_level: Optional[float] = None
    processing_time_seconds: Optional[int] = None
    validation_time: Optional[str] = None
    system_metrics: Optional[SystemMetrics] = None


class AlertData(BaseModel):
    alert_details: Optional[str] = None
    alert_time: Optional[str] = None
    load_setpoint: Optional[int] = None
    generation_setpoint: Optional[int] = None
    predicted_security_state: Optional[str] = None
    confidence_bound: Optional[float] = None


class ReviewData(BaseModel):
    review_time_seconds: Optional[int] = None
    detections_confirmed: Optional[int] = None
    false_positives_identified: Optional[int] = None
    false_negatives_identified: Optional[int] = None
    feedback_details: Optional[str] = None
    time_spent_on_corrections_seconds: Optional[int] = None
    discrepancy_rate: Optional[float] = None
    operator_decision: Optional[str] = None
    feedback_time: Optional[str] = None
    insecure_instances_confirmed: Optional[int] = None
    false_positives: Optional[int] = None
    false_negatives: Optional[int] = None
    user_satisfaction: Optional[str] = None
    feedback_provided: Optional[str] = None
    human_confirmation_rate: Optional[float] = None


class RetrainingDetails(BaseModel):
    time_taken_seconds: Optional[int] = None
    data_used: Optional[str] = None
    ai_model_version_after_retraining: Optional[str] = None


class RetrainEvent(BaseModel):
    retraining_time: Optional[str] = None
    initial_metrics: Optional[Dict[str, float]] = None
    post_retraining_metrics: Optional[Dict[str, float]] = None
    retraining_details: Optional[RetrainingDetails] = None


class PerformanceInfrastructure(BaseModel):
    hardware_specifications: Optional[str] = None
    software_stack: Optional[str] = None
    network_conditions: Optional[str] = None


class PerformanceLogs(BaseModel):
    processing_time_seconds: Optional[Dict[str, Union[int, float]]] = None
    resource_utilization: Optional[Dict[str, Union[int, float]]] = None
    human_effort_seconds: Optional[Dict[str, Union[int, float]]] = None


class AIModelData(BaseModel):
    ai_model_name: Optional[str] = None
    training_data: Optional[str] = None
    ai_model_size: Optional[str] = None
    inference_time_seconds: Optional[Union[int, float]] = None
    deployment_details: Optional[str] = None


class InteractionData(BaseModel):
    image_id: Optional[str] = None
    presentation_time: Optional[str] = None
    validation_data: Optional[ValidationData] = None
    review_data: Optional[ReviewData] = None
    application_id: Optional[str] = None
    justification_documents: Optional[str] = None
    submission_time: Optional[str] = None
    load_generation_data: Optional[List[Dict[str, Union[str, int, float]]]] = None
    alert_data: Optional[Union[AlertData, List[AlertData]]] = None


class LogSchema(BaseModel):
    session_id: str
    user_id: str
    ai_model_version: Optional[str] = None
    app_version: str
    start_time: str
    end_time: str
    interaction_data: Optional[InteractionData] = None
    retrain_events: Optional[List[RetrainEvent]] = None
    performance_infrastructure: Optional[PerformanceInfrastructure] = None
    performance_logs: Optional[PerformanceLogs] = None
    ai_model_data: Optional[AIModelData] = None
    decisions: Optional[List[Dict[str, Any]]] = None
