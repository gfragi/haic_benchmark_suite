from datetime import datetime, timedelta
import random
import uuid
from fastapi import HTTPException
from app.utils.generic_functions import random_date

def generate_simple_unique_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"

# Template with placeholders to be dynamically replaced
logs_templates = {
    "dss_img_recog": {
        "interaction_data": {
            "image_id": "img-" + str(uuid.uuid4()),  # Unique ID for each image
            "presentation_time": lambda: random_date(datetime.now() - timedelta(days=1), datetime.now()).isoformat(),
            "result": lambda: random.choice(["true_positive", "false_positive", "true_negative", "false_negative"]),
            "ai_detection_results": lambda: random.choice(["true_positive", "false_positive", "true_negative", "false_negative"]),
            "outcome": lambda: random.choice(["correct", "incorrect"]),
            "performance_at_t": lambda: random.uniform(0.7, 0.9),
            "performance_at_t_1": lambda: random.uniform(0.6, 0.7),
            "time_interval": lambda: random.randint(1800, 7200),  # Time interval in seconds

            # Efficiency metrics
            "response_time": lambda: random.uniform(100, 500),  # Response time in milliseconds
            "performance_improvement": lambda: random.uniform(0.01, 0.1),
            "time_spent": lambda: random.randint(1000, 5000),  # Time spent in seconds
            "reached_target": lambda: random.choice([True, False]),
            "resources_used": lambda: random.randint(20, 100),
            "total_resources": 100,  # Assuming a fixed maximum resource value for simplicity
            "time_without_ai": lambda: random.randint(300, 600),
            "time_with_ai": lambda: random.randint(150, 400),
            "correction_effectiveness": lambda: random.uniform(0.5, 1.0),
            "correction_time": lambda: random.randint(50, 200),
            "errors_before": lambda: random.randint(5, 15),
            "errors_after": lambda: random.randint(0, 10),
            "pre_retention_performance": lambda: random.uniform(0.6, 0.8),
            "post_retention_performance": lambda: random.uniform(0.75, 0.9),

            # Adaptability and Learning metrics
            "pre_feedback_performance": lambda: random.uniform(0.6, 0.7),
            "post_feedback_performance": lambda: random.uniform(0.7, 0.85),
            "pre_adaptation_performance": lambda: random.uniform(0.6, 0.75),
            "post_adaptation_performance": lambda: random.uniform(0.75, 0.85),
            "pre_correction_performance": lambda: random.uniform(0.6, 0.8),
            "post_correction_performance": lambda: random.uniform(0.75, 0.9),
            "learning_gain": lambda: random.uniform(0.01, 0.05),
            "learning_time": lambda: random.randint(200, 1000),
            "objective_status": lambda: random.choice(["achieved", "not achieved"]),

            # Collaboration and Interaction metrics
            "human_decision": lambda: random.choice(["approve", "reject"]),
            "ai_suggestion": lambda: random.choice(["approve", "reject"]),
            "ai_assisted": lambda: random.choice([True, False]),
            "decision_outcome": lambda: random.choice(["successful", "unsuccessful"]),
            "resolution_time": lambda: random.randint(50, 300),
            "effort_without_ai": lambda: random.randint(5, 15),
            "effort_with_ai": lambda: random.randint(1, 10),

            # Trust and Safety metrics
            "confidence_level": lambda: random.uniform(0.0, 1.0),
            "trust_rating": lambda: random.randint(6, 10),
            "trust_scale_maximum": 10,
            "safety_incidents": lambda: random.randint(0, 2),
            "uptime": lambda: random.randint(4500, 5000),
            "total_time": 6000,

            # Robustness and Generalization metrics
            "performance_adversarial": lambda: random.uniform(0.6, 0.8),
            "performance_normal": lambda: random.uniform(0.8, 0.95),
            "performance_across_domains": lambda: random.uniform(0.7, 0.9),
            "baseline_performance": lambda: random.uniform(0.65, 0.8),
        },
        "retrain_events": [
            {
                "retraining_time": lambda: random_date(datetime.now() - timedelta(days=365), datetime.now()).isoformat(),
                "initial_metrics": {
                    "detection_accuracy": lambda: random.uniform(0.6, 0.8),
                    "false_positive_rate": lambda: random.uniform(0.05, 0.15),
                    "false_negative_rate": lambda: random.uniform(0.05, 0.15),
                },
                "post_retraining_metrics": {
                    "detection_accuracy": lambda: random.uniform(0.8, 0.95),
                    "false_positive_rate": lambda: random.uniform(0.02, 0.1),
                    "false_negative_rate": lambda: random.uniform(0.02, 0.1),
                },
                "retraining_details": {
                    "time_taken_seconds": lambda: random.randint(1800, 7200),  # Retraining time in seconds
                    "data_used": "feedback and corrections from the review",
                    "ai_model_version_after_retraining": lambda: f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                },
            }
        ]
    },
    # Additional templates for dss_smart_cities, dss_smart_energy, etc. can follow the same structure.
}

# Log generation function with dynamic field generation
def generate_log(app_type: str, start_datetime: str, end_datetime: str, ai_model_version_range: str, custom_data=None):
    if app_type not in logs_templates:
        raise ValueError(f"Unsupported app type: {app_type}")

    start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%SZ')
    end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%SZ')
    ai_model_version_start, ai_model_version_end = ai_model_version_range.split('-')

    session_start = random_date(start_datetime, end_datetime)
    session_end = random_date(session_start, end_datetime)

    log = {
        "session_id": generate_simple_unique_id(app_type),
        "user_id": generate_simple_unique_id(app_type),
        "ai_model_version": f"{random.randint(int(ai_model_version_start[0]), int(ai_model_version_end[0]))}.{random.randint(int(ai_model_version_start[2]), int(ai_model_version_end[2]))}.{random.randint(int(ai_model_version_start[4]), int(ai_model_version_end[4]))}",
        "app_version": "1.0.0",
        "start_time": session_start.isoformat() + 'Z',
        "end_time": session_end.isoformat() + 'Z',
    }

    # Populate interaction data with dynamic values
    interaction_data = logs_templates[app_type]["interaction_data"]
    log["interaction_data"] = {
        key: (custom_data[key] if custom_data and key in custom_data else (value() if callable(value) else value))
        for key, value in interaction_data.items()
    }

    # Populate retrain events with dynamic values
    retrain_events_template = logs_templates[app_type]["retrain_events"]
    log["retrain_events"] = [
        {
            "retraining_time": event["retraining_time"](),
            "initial_metrics": {k: (v() if callable(v) else v) for k, v in event["initial_metrics"].items()},
            "post_retraining_metrics": {k: (v() if callable(v) else v) for k, v in event["post_retraining_metrics"].items()},
            "retraining_details": {k: (v() if callable(v) else v) for k, v in event["retraining_details"].items()}
        }
        for event in retrain_events_template
    ]

    return log