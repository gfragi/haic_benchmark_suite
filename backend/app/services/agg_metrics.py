import datetime
from sqlalchemy.orm import Session
from app.models import LogEntry, EvaluationConfig, EvaluationResult
from app.services.evaluate import calculate_prediction_accuracy, calculate_precision, calculate_recall, calculate_human_ai_agreement_rate, calculate_time_to_resolution, calculate_human_effort_saved, calculate_ai_assistance_rate, calculate_learning_efficiency, calculate_correction_efficiency

def calculate_aggregated_metrics(logs):
    """
    Calculate aggregated metrics across multiple logs.
    """
    metrics_aggregated = {
        "accuracy": [],
        "precision": [],
        "recall": [],
        "human_ai_agreement_rate": [],
        "time_to_resolution": [],
        "human_effort_saved": [],
        "ai_assistance_rate": [],
        "learning_efficiency": [],
        "correction_efficiency": []
    }

    # Aggregate the metrics from each log
    for log in logs:
        interaction_data = log.interaction_data

        metrics_aggregated["accuracy"].append(calculate_prediction_accuracy(interaction_data))
        metrics_aggregated["precision"].append(calculate_precision(interaction_data))
        metrics_aggregated["recall"].append(calculate_recall(interaction_data))
        metrics_aggregated["human_ai_agreement_rate"].append(calculate_human_ai_agreement_rate(interaction_data))
        metrics_aggregated["time_to_resolution"].append(calculate_time_to_resolution(interaction_data))
        metrics_aggregated["human_effort_saved"].append(calculate_human_effort_saved(interaction_data))
        metrics_aggregated["ai_assistance_rate"].append(calculate_ai_assistance_rate(interaction_data))
        metrics_aggregated["learning_efficiency"].append(calculate_learning_efficiency(interaction_data))
        metrics_aggregated["correction_efficiency"].append(calculate_correction_efficiency(interaction_data))

    # Calculate the average or final aggregated metric
    aggregated_metrics = {key: sum(values) / len(values) if values else 0 for key, values in metrics_aggregated.items()}

    return aggregated_metrics

def save_evaluation_result(db: Session, configuration_id: int, aggregated_metrics: dict):
    """
    Save the calculated metrics to the database.
    """
    result = EvaluationResult(
        configuration_id=configuration_id,
        accuracy=aggregated_metrics["accuracy"],
        precision=aggregated_metrics["precision"],
        recall=aggregated_metrics["recall"],
        human_ai_agreement_rate=aggregated_metrics["human_ai_agreement_rate"],
        time_to_resolution=aggregated_metrics["time_to_resolution"],
        human_effort_saved=aggregated_metrics["human_effort_saved"],
        ai_assistance_rate=aggregated_metrics["ai_assistance_rate"],
        learning_efficiency=aggregated_metrics["learning_efficiency"],
        correction_efficiency=aggregated_metrics["correction_efficiency"],
        evaluation_date=datetime.datetime.utcnow()
    )

    db.add(result)
    db.commit()