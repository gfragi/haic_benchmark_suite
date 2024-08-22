from pydantic import BaseModel
from typing import Dict, List, Optional

class SystemMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float

class ValidationData(BaseModel):
    validation_results: str
    confidence_level: float
    processing_time_seconds: int
    validation_time: str
    system_metrics: SystemMetrics

class AlertData(BaseModel):
    alert_details: str
    confidence_level: float
    alert_time: str

class ReviewData(BaseModel):
    review_time_seconds: int
    discrepancy_rate: float
    operator_decision: str
    feedback_time: str

class FeedbackData(BaseModel):
    feedback_details: str
    correction_actions: str
    feedback_time: str

class InteractionData(BaseModel):
    application_id: str
    justification_documents: str
    submission_time: str
    validation_data: ValidationData
    alert_data: Optional[AlertData] = None
    review_data: Optional[ReviewData] = None
    feedback_data: Optional[FeedbackData] = None

class InitialMetrics(BaseModel):
    detection_accuracy: float
    false_positive_rate: float
    false_negative_rate: float

class PostRetrainingMetrics(BaseModel):
    detection_accuracy: float
    false_positive_rate: float
    false_negative_rate: float

class RetrainingDetails(BaseModel):
    time_taken_seconds: int
    data_used: str
    ai_model_version_after_retraining: str

class RetrainEvent(BaseModel):
    retraining_time: str
    initial_metrics: InitialMetrics
    post_retraining_metrics: PostRetrainingMetrics
    retraining_details: RetrainingDetails

class PerformanceInfrastructure(BaseModel):
    hardware_specifications: str
    software_stack: str
    network_conditions: str

class PerformanceLogs(BaseModel):
    processing_time_seconds: Dict[str, int]
    resource_utilization: Dict[str, int]
    human_effort_seconds: Dict[str, int]

class AIModelData(BaseModel):
    ai_model_name: str
    training_data: str
    model_size: str
    inference_time_seconds: int
    deployment_details: str

class LogSchema(BaseModel):
    session_id: str
    user_id: str
    ai_model_version: str
    app_version: str
    start_time: str
    end_time: str
    interaction_data: InteractionData
    retrain_events: List[RetrainEvent]
    performance_infrastructure: PerformanceInfrastructure
    performance_logs: PerformanceLogs
    ai_model_data: AIModelData
    evaluation_config_id: Optional[int] = None  # To link with the evaluation configuration

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "unique_session_id",
                "user_id": "unique_user_id",
                "ai_model_version": "1.0.0",
                "app_version": "1.0.0",
                "start_time": "2024-06-28T12:00:00Z",
                "end_time": "2024-06-28T12:30:00Z",
                "interaction_data": {
                    "application_id": "unique_application_id",
                    "justification_documents": "document_list",
                    "submission_time": "2024-06-28T12:00:00Z",
                    "validation_data": {
                        "validation_results": "accepted",
                        "confidence_level": 0.85,
                        "processing_time_seconds": 300,
                        "validation_time": "2024-06-28T12:05:00Z",
                        "system_metrics": {
                            "accuracy": 0.9,
                            "precision": 0.85,
                            "recall": 0.88
                        }
                    },
                    "alert_data": {
                        "alert_details": "reason_for_alert",
                        "confidence_level": 0.85,
                        "alert_time": "2024-06-28T12:06:00Z"
                    },
                    "review_data": {
                        "review_time_seconds": 600,
                        "discrepancy_rate": 0.05,
                        "operator_decision": "confirm",
                        "feedback_time": "2024-06-28T12:16:00Z"
                    },
                    "feedback_data": {
                        "feedback_details": "details_of_feedback",
                        "correction_actions": "suggested_corrections",
                        "feedback_time": "2024-06-28T12:18:00Z"
                    }
                },
                "retrain_events": [
                    {
                        "retraining_time": "2024-06-29T12:00:00Z",
                        "initial_metrics": {
                            "detection_accuracy": 0.75,
                            "false_positive_rate": 0.10,
                            "false_negative_rate": 0.05
                        },
                        "post_retraining_metrics": {
                            "detection_accuracy": 0.85,
                            "false_positive_rate": 0.05,
                            "false_negative_rate": 0.03
                        },
                        "retraining_details": {
                            "time_taken_seconds": 7200,
                            "data_used": "feedback and corrections from the session",
                            "ai_model_version_after_retraining": "1.1.0"
                        }
                    }
                ],
                "performance_infrastructure": {
                    "hardware_specifications": "details_of_hardware",
                    "software_stack": "details_of_software",
                    "network_conditions": "details_of_network_conditions"
                },
                "performance_logs": {
                    "processing_time_seconds": {
                        "with_ai": 300,
                        "without_ai": 600
                    },
                    "resource_utilization": {
                        "with_ai": 100,
                        "without_ai": 200
                    },
                    "human_effort_seconds": {
                        "with_ai": 600,
                        "without_ai": 1800
                    }
                },
                "ai_model_data": {
                    "ai_model_name": "ai_model_name",
                    "training_data": "details_of_training_data",
                    "model_size": "size_of_model",
                    "inference_time_seconds": 2,
                    "deployment_details": "details_of_deployment"
                },
                "evaluation_config_id": 1  # Example of association with an evaluation configuration
            }
        }
