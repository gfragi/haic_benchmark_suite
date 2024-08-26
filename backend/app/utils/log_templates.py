from datetime import datetime, timedelta
import random
import uuid

from fastapi import HTTPException

logs_templates = {
    "radiologist": {
        "interaction_data": {
            "image_id": "unique_image_id",
            "presentation_time": "2024-07-01T09:01:00Z",
            "result": "true_positive",
            "response_time": 120,
            "performance_improvement": 15,
            "time_spent": 5,
            "outcome": "correct",
            "objective_status": "achieved",
            "pre_feedback_performance": 80,
            "post_feedback_performance": 85,
            "pre_adaptation_performance": 78,
            "post_adaptation_performance": 82,
            "reached_target_accuracy": True,
            "errors_before": 5,
            "errors_after": 2,
            "confidence_level": 0.95,
            "performance_at_t": 0.9,
            "performance_at_t_1": 0.85,
            "time_interval": 5,
            "resources_used": 120,
            "total_resources": 150,
            "pre_correction_performance": 75,
            "post_correction_performance": 85,
            "decision_outcome": "successful",
            "pre_retention_performance": 90,
            "post_retention_performance": 85,
            "time_without_ai": 300,
            "time_with_ai": 200,
            "trust_rating": 8,
            "trust_scale_maximum": 10,
            "safety_incidents": 0,
            "performance_adversarial": 0.85,
            "performance_normal": 0.9,
            "performance_across_domains": 0.88,
            "baseline_performance": 0.9,
            "uptime": 99.9,
            "total_time": 100,
            "validation_data": {
                "ai_detection_results": "detection_summary",
                "confidence_scores": {
                    "detection_1": 0.85,
                    "detection_2": 0.9
                },
                "processing_time_seconds": 180,
                "validation_time": "2024-07-01T09:03:00Z",
                "system_metrics": {
                    "accuracy": 0.88,
                    "precision": 0.86,
                    "recall": 0.9
                }
            },
            "review_data": {
                "review_time_seconds": 300,
                "detections_confirmed": 5,
                "false_positives_identified": 2,
                "false_negatives_identified": 1,
                "feedback_details": "detailed_feedback_provided",
                "time_spent_on_corrections_seconds": 120
            }
        },
        "retrain_events": [
            {
                "retraining_time": "2024-07-02T09:00:00Z",
                "initial_metrics": {
                    "detection_accuracy": 0.75,
                    "false_positive_rate": 0.10,
                    "false_negative_rate": 0.08
                },
                "post_retraining_metrics": {
                    "detection_accuracy": 0.85,
                    "false_positive_rate": 0.05,
                    "false_negative_rate": 0.04
                },
                "retraining_details": {
                    "time_taken_seconds": 3600,
                    "data_used": "feedback and corrections from the review",
                    "model_version_after_retraining": "1.1.0"
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
                "with_ai": random.randint(100, 300),
                "without_ai": random.randint(300, 600)
            },
            "resource_utilization": {
                "with_ai": random.randint(50, 100),
                "without_ai": random.randint(100, 200)
            },
            "human_effort_seconds": {
                "with_ai": random.randint(300, 900),
                "without_ai": random.randint(600, 1800)
            }
        },
        "ai_model_data": {
            "model_name": "detection_model_name",
            "training_data": "details_of_training_data",
            "model_size": "size_of_model",
            "inference_time_seconds": random.randint(1, 5),
            "deployment_details": "details_of_deployment"
        }
    },
    "smart_cities": {
        "interaction_data": {
            "application_id": "unique_application_id",
            "justification_documents": "document_list",
            "submission_time": "2024-06-28T12:00:00Z",
            "validation_data": {
                "validation_results": "accepted/rejected",
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
                "operator_decision": "confirm/reject",
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
                    "model_version_after_retraining": "1.1.0"
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
                "with_ai": random.randint(200, 600),
                "without_ai": random.randint(400, 900)
            },
            "resource_utilization": {
                "with_ai": random.randint(100, 200),
                "without_ai": random.randint(200, 400)
            },
            "human_effort_seconds": {
                "with_ai": random.randint(300, 900),
                "without_ai": random.randint(900, 2700)
            }
        },
        "ai_model_data": {
            "model_name": "model_name",
            "training_data": "details_of_training_data",
            "model_size": "size_of_model",
            "inference_time_seconds": random.randint(1, 5),
            "deployment_details": "details_of_deployment"
        }
    },
    "smart_energy": {
        "interaction_data": {
            "load_generation_data": [
                {
                    "timestamp": "2024-07-10T10:01:00Z",
                    "load_setpoint": 150,
                    "generation_setpoint": 140,
                    "security_state": "secure",
                    "predicted_security_state": "insecure",
                    "confidence_bound": 0.75
                },
                {
                    "timestamp": "2024-07-10T10:05:00Z",
                    "load_setpoint": 155,
                    "generation_setpoint": 150,
                    "security_state": "secure",
                    "predicted_security_state": "secure",
                    "confidence_bound": 0.90
                }
            ],
            "alert_data": [
                {
                    "alert_time": "2024-07-10T10:02:00Z",
                    "load_setpoint": 150,
                    "generation_setpoint": 140,
                    "predicted_security_state": "insecure",
                    "confidence_bound": 0.75
                }
            ],
            "review_data": {
                "review_time_seconds": 300,
                "insecure_instances_confirmed": 1,
                "false_positives": 0,
                "false_negatives": 1,
                "user_satisfaction": "high",
                "feedback_provided": "detailed_feedback",
                "time_spent_on_corrections_seconds": 120,
                "human_confirmation_rate": 0.95
            }
        },
        "retrain_events": [
            {
                "retraining_time": "2024-07-11T10:00:00Z",
                "initial_metrics": {
                    "detection_accuracy": 0.80,
                    "false_positive_rate": 0.05,
                    "false_negative_rate": 0.10
                },
                "post_retraining_metrics": {
                    "detection_accuracy": 0.90,
                    "false_positive_rate": 0.03,
                    "false_negative_rate": 0.05
                },
                "retraining_details": {
                    "time_taken_seconds": 3600,
                    "data_used": "feedback and simulation results",
                    "model_version_after_retraining": "1.1.0"
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
                "with_ai": random.randint(100, 300),
                "without_ai": random.randint(300, 600)
            },
            "resource_utilization": {
                "with_ai": random.randint(50, 100),
                "without_ai": random.randint(100, 200)
            },
            "human_effort_seconds": {
                "with_ai": random.randint(300, 900),
                "without_ai": random.randint(600, 1800)
            }
        },
        "ai_model_data": {
            "model_name": "grid_security_model",
            "training_data": "details_of_training_data",
            "model_size": "size_of_model",
            "inference_time_seconds": random.randint(1, 5),
            "deployment_details": "details_of_deployment"
        }
    }
}

def generate_unique_id():
    return str(uuid.uuid4())

def random_date(start, end):
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randrange(int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def generate_log(app_type: str, start_datetime: str, end_datetime: str, model_version_range: str):
    if app_type not in logs_templates:
        raise ValueError(f"Unsupported app type: {app_type}")

    start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%SZ')
    end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%SZ')
    model_version_start, model_version_end = model_version_range.split('-')

    session_start = random_date(start_datetime, end_datetime)
    session_end = random_date(session_start, end_datetime)

    log = {
        "session_id": generate_unique_id(),
        "user_id": generate_unique_id(),
        "model_version": f"{random.randint(int(model_version_start[0]), int(model_version_end[0]))}.{random.randint(int(model_version_start[2]), int(model_version_end[2]))}.{random.randint(int(model_version_start[4]), int(model_version_end[4]))}",
        "app_version": "1.0.0",
        "start_time": session_start.isoformat() + 'Z',
        "end_time": session_end.isoformat() + 'Z',
    }

    # Now add the specific interaction data based on the app type
    if app_type == "radiologist":
        log.update(logs_templates["radiologist"])

    elif app_type == "smart_cities":
        log.update(logs_templates["smart_cities"])

    elif app_type == "smart_energy":
        log.update(logs_templates["smart_energy"])

    return log
