from datetime import datetime, timedelta
import random
import uuid

from fastapi import HTTPException


logs_templates = {
    "radiologist": {
    "session_id": "unique_session_id",
    "user_id": "unique_user_id",
    "model_version": "1.0.0",
    "app_version": "1.0.0",
    "start_time": "2024-07-01T09:00:00Z",
    "end_time": "2024-07-01T09:45:00Z",
    "interaction_data": {
      "image_id": "unique_image_id",
      "presentation_time": "2024-07-01T09:01:00Z",
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
        "with_ai": 180,
        "without_ai": 360
      },
      "resource_utilization": {
        "with_ai": 80,
        "without_ai": 160
      },
      "human_effort_seconds": {
        "with_ai": 600,
        "without_ai": 1200
      }
    },
    "ai_model_data": {
      "model_name": "detection_model_name",
      "training_data": "details_of_training_data",
      "model_size": "size_of_model",
      "inference_time_seconds": 2,
      "deployment_details": "details_of_deployment"
    }
  },
    
    
    "smart_cities": {
    "session_id": "unique_session_id",
    "user_id": "unique_user_id",
    "model_version": "1.0.0",
    "app_version": "1.0.0",
    "start_time": "2024-06-28T12:00:00Z",
    "end_time": "2024-06-28T12:30:00Z",
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
      "model_name": "model_name",
      "training_data": "details_of_training_data",
      "model_size": "size_of_model",
      "inference_time_seconds": 2,
      "deployment_details": "details_of_deployment"
    }
  },



    "smart_energy": {
    "session_id": "unique_session_id",
    "user_id": "unique_user_id",
    "model_version": "1.0.0",
    "app_version": "1.0.0",
    "start_time": "2024-07-10T10:00:00Z",
    "end_time": "2024-07-10T10:30:00Z",
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
        "with_ai": 200,
        "without_ai": 400
      },
      "resource_utilization": {
        "with_ai": 80,
        "without_ai": 160
      },
      "human_effort_seconds": {
        "with_ai": 600,
        "without_ai": 1200
      }
    },
    "ai_model_data": {
      "model_name": "grid_security_model",
      "training_data": "details_of_training_data",
      "model_size": "size_of_model",
      "inference_time_seconds": 1,
      "deployment_details": "details_of_deployment"
    }
  }
}

def generate_unique_id():
    return str(uuid.uuid4())

def random_date(start, end):
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randrange(delta.total_seconds())
    return start + timedelta(seconds=random_seconds)

def generate_log(app_type: str, start_datetime: str, end_datetime: str, model_version_range: str):
    if app_type not in logs_templates:
        raise ValueError(f"Unsupported app type: {app_type}")

    start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%SZ')
    end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%SZ')
    model_version_start, model_version_end = model_version_range.split('-')

    session_start = random_date(start_datetime, end_datetime)
    session_end = random_date(session_start, end_datetime)

    # Version split it into two parts
    try:
        model_version_start, model_version_end = model_version_range.split('-')
        model_version_start = model_version_start.strip()
        model_version_end = model_version_end.strip()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model_version_range format")


    log = {
        "session_id": generate_unique_id(),
        "user_id": generate_unique_id(),
        "model_version": f"{random.randint(int(model_version_start[0]), int(model_version_end[0]))}.{random.randint(int(model_version_start[2]), int(model_version_end[2]))}.{random.randint(int(model_version_start[4]), int(model_version_end[4]))}",
        "app_version": "1.0.0",
        "start_time": session_start.isoformat() + 'Z',
        "end_time": session_end.isoformat() + 'Z',
    }


    if app_type == "radiologist":
        log.update({
        "interaction_data": {
            "image_id": generate_unique_id(),
            "presentation_time": (session_start + timedelta(minutes=1)).isoformat() + 'Z',
            "validation_data": {
                "ai_detection_results": "detection_summary",
                "confidence_scores": {
                    "detection_1": round(random.uniform(0.7, 1.0), 2),
                    "detection_2": round(random.uniform(0.7, 1.0), 2)
                },
                "processing_time_seconds": random.randint(100, 300),
                "validation_time": (session_start + timedelta(minutes=3)).isoformat() + 'Z',
                "system_metrics": {
                    "accuracy": round(random.uniform(0.7, 1.0), 2),
                    "precision": round(random.uniform(0.7, 1.0), 2),
                    "recall": round(random.uniform(0.7, 1.0), 2)
                }
            },
            "review_data": {
                "review_time_seconds": random.randint(200, 600),
                "detections_confirmed": random.randint(3, 10),
                "false_positives_identified": random.randint(0, 5),
                "false_negatives_identified": random.randint(0, 5),
                "feedback_details": "detailed_feedback_provided",
                "time_spent_on_corrections_seconds": random.randint(60, 300)
            }
        },
        "retrain_events": [{
            "retraining_time": (session_end + timedelta(days=1)).isoformat() + 'Z',
            "initial_metrics": {
                "detection_accuracy": round(random.uniform(0.65, 0.85), 2),
                "false_positive_rate": round(random.uniform(0.05, 0.15), 2),
                "false_negative_rate": round(random.uniform(0.04, 0.1), 2)
            },
            "post_retraining_metrics": {
                "detection_accuracy": round(random.uniform(0.85, 0.95), 2),
                "false_positive_rate": round(random.uniform(0.01, 0.05), 2),
                "false_negative_rate": round(random.uniform(0.02, 0.05), 2)
            },
            "retraining_details": {
                "time_taken_seconds": random.randint(1800, 7200),
                "data_used": "feedback and corrections from the review",
                "model_version_after_retraining": f"{random.randint(1,4)}.{random.randint(0,9)}.{random.randint(0,9)}"
            }
        }],
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
    })

    if app_type == "smart_cities":
        log.update({
        "interaction_data": {
            "application_id": generate_unique_id(),
            "justification_documents": "document_list",
            "submission_time": session_start.isoformat() + 'Z',
            "validation_data": {
                "validation_results": "accepted/rejected",
                "confidence_level": round(random.uniform(0.7, 1.0), 2),
                "processing_time_seconds": random.randint(200, 600),
                "validation_time": (session_start + timedelta(minutes=5)).isoformat() + 'Z',
                "system_metrics": {
                    "accuracy": round(random.uniform(0.7, 1.0), 2),
                    "precision": round(random.uniform(0.7, 1.0), 2),
                    "recall": round(random.uniform(0.7, 1.0), 2)
                }
            },
            "alert_data": {
                "alert_details": "reason_for_alert",
                "confidence_level": round(random.uniform(0.7, 1.0), 2),
                "alert_time": (session_start + timedelta(minutes=6)).isoformat() + 'Z'
            },
            "review_data": {
                "review_time_seconds": random.randint(300, 900),
                "discrepancy_rate": round(random.uniform(0.01, 0.1), 2),
                "operator_decision": "confirm/reject",
                "feedback_time": (session_start + timedelta(minutes=16)).isoformat() + 'Z'
            },
            "feedback_data": {
                "feedback_details": "details_of_feedback",
                "correction_actions": "suggested_corrections",
                "feedback_time": (session_start + timedelta(minutes=18)).isoformat() + 'Z'
            }
        },
        "retrain_events": [{
            "retraining_time": (session_end + timedelta(days=1)).isoformat() + 'Z',
            "initial_metrics": {
                "detection_accuracy": round(random.uniform(0.65, 0.85), 2),
                "false_positive_rate": round(random.uniform(0.05, 0.15), 2),
                "false_negative_rate": round(random.uniform(0.02, 0.08), 2)
            },
            "post_retraining_metrics": {
                "detection_accuracy": round(random.uniform(0.85, 0.95), 2),
                "false_positive_rate": round(random.uniform(0.01, 0.05), 2),
                "false_negative_rate": round(random.uniform(0.01, 0.05), 2)
            },
            "retraining_details": {
                "time_taken_seconds": random.randint(3600, 7200),
                "data_used": "feedback and corrections from the session",
                "model_version_after_retraining": f"{random.randint(1,4)}.{random.randint(0,9)}.{random.randint(0,9)}"
            }
        }],
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
    })

    if app_type == "smart_energy":
        log.update({
        "interaction_data": {
            "load_generation_data": [
                {
                    "timestamp": (session_start + timedelta(minutes=1)).isoformat() + 'Z',
                    "load_setpoint": random.randint(100, 200),
                    "generation_setpoint": random.randint(100, 200),
                    "security_state": "secure",
                    "predicted_security_state": "insecure",
                    "confidence_bound": round(random.uniform(0.7, 1.0), 2)
                },
                {
                    "timestamp": (session_start + timedelta(minutes=5)).isoformat() + 'Z',
                    "load_setpoint": random.randint(100, 200),
                    "generation_setpoint": random.randint(100, 200),
                    "security_state": "secure",
                    "predicted_security_state": "secure",
                    "confidence_bound": round(random.uniform(0.7, 1.0), 2)
                }
            ],
            "alert_data": [
                {
                    "alert_time": (session_start + timedelta(minutes=2)).isoformat() + 'Z',
                    "load_setpoint": random.randint(100, 200),
                    "generation_setpoint": random.randint(100, 200),
                    "predicted_security_state": "insecure",
                    "confidence_bound": round(random.uniform(0.7, 1.0), 2)
                }
            ],
            "review_data": {
                "review_time_seconds": random.randint(200, 600),
                "insecure_instances_confirmed": random.randint(0, 5),
                "false_positives": random.randint(0, 3),
                "false_negatives": random.randint(0, 3),
                "user_satisfaction": "high",
                "feedback_provided": "detailed_feedback",
                "time_spent_on_corrections_seconds": random.randint(60, 300),
                "human_confirmation_rate": round(random.uniform(0.8, 1.0), 2)
            }
        },
        "retrain_events": [{
            "retraining_time": (session_end + timedelta(days=1)).isoformat() + 'Z',
            "initial_metrics": {
                "detection_accuracy": round(random.uniform(0.7, 0.9), 2),
                "false_positive_rate": round(random.uniform(0.01, 0.1), 2),
                "false_negative_rate": round(random.uniform(0.01, 0.1), 2)
            },
            "post_retraining_metrics": {
                "detection_accuracy": round(random.uniform(0.8, 1.0), 2),
                "false_positive_rate": round(random.uniform(0.01, 0.05), 2),
                "false_negative_rate": round(random.uniform(0.01, 0.05), 2)
            },
            "retraining_details": {
                "time_taken_seconds": random.randint(1800, 7200),
                "data_used": "feedback and simulation results",
                "model_version_after_retraining": f"{random.randint(1,4)}.{random.randint(0,9)}.{random.randint(0,9)}"
            }
        }],
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
    })


    return log