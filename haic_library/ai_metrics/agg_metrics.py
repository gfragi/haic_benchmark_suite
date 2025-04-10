import datetime
from sqlalchemy.orm import Session
from app.models import LogEntry, EvaluationConfig, EvaluationResult
from app.services.metrics import Metrics

def calculate_metrics_for_group(db: Session, config_id: int, group_name: str):
    """
    Calculate metrics for a specific group of logs.
    """
    # Fetch logs for the configuration and group
    logs = db.query(LogEntry).filter(LogEntry.configuration_id == config_id).all()

    if not logs:
        # If no logs are found, return None or handle it accordingly
        return None

    # Mapping of group names to their respective metric methods
    metrics_map = {
        "Effectiveness": [
            Metrics.Effectiveness.calculate_prediction_accuracy,
            Metrics.Effectiveness.calculate_precision,
            Metrics.Effectiveness.calculate_recall,
            Metrics.Effectiveness.calculate_overall_system_accuracy,
            Metrics.Effectiveness.calculate_model_improvement_rate,
        ],
        "Efficiency": [
            Metrics.Efficiency.calculate_response_time,
            Metrics.Efficiency.calculate_teaching_efficiency,
            Metrics.Efficiency.calculate_query_efficiency,
            Metrics.Efficiency.calculate_resource_utilization,
            Metrics.Efficiency.calculate_task_completion_time,
            Metrics.Efficiency.calculate_correction_efficiency,
            Metrics.Efficiency.calculate_error_reduction_rate,
            Metrics.Efficiency.calculate_knowledge_retention,
        ],
        "Adaptability and Learning": [
            Metrics.AdaptabilityAndLearning.calculate_feedback_impact,
            Metrics.AdaptabilityAndLearning.calculate_adaptability_score,
            Metrics.AdaptabilityAndLearning.calculate_impact_of_corrections,
            Metrics.AdaptabilityAndLearning.calculate_learning_efficiency,
            Metrics.AdaptabilityAndLearning.calculate_objective_fulfillment_rate,
        ],
        "Collaboration and Interaction": [
            Metrics.CollaborationAndInteraction.calculate_human_ai_agreement_rate,
            Metrics.CollaborationAndInteraction.calculate_ai_assistance_rate,
            Metrics.CollaborationAndInteraction.calculate_decision_effectiveness,
            Metrics.CollaborationAndInteraction.calculate_time_to_resolution,
            Metrics.CollaborationAndInteraction.calculate_human_effort_saved,
        ],
        "Trust and Safety": [
            Metrics.TrustAndSafety.calculate_confidence,
            Metrics.TrustAndSafety.calculate_trust_score,
            Metrics.TrustAndSafety.calculate_safety_incidents,
            Metrics.TrustAndSafety.calculate_system_reliability,
        ],
        "Robustness and Generalization": [
            Metrics.RobustnessAndGeneralization.calculate_adversarial_robustness,
            Metrics.RobustnessAndGeneralization.calculate_domain_generalization,
        ],
    }

    # Initialize the result dictionary
    results = {}

    # Calculate and aggregate metrics for the selected group
    for metric_function in metrics_map.get(group_name, []):
        metric_name = metric_function.__name__.replace("calculate_", "").replace("_", " ").title()
        results[metric_name] = [metric_function(log.interaction_data) for log in logs]

    # Aggregate the results (e.g., average, sum, etc.)
    aggregated_results = {
        metric: sum(values) / len(values) if values else 0
        for metric, values in results.items()
    }

    return aggregated_results

def save_evaluation_result(db: Session, configuration_id: int, aggregated_metrics: dict):
    """
    Save the calculated metrics to the database.
    """
    result = EvaluationResult(
        configuration_id=configuration_id,
        accuracy=aggregated_metrics.get("Prediction Accuracy", 0),
        precision=aggregated_metrics.get("Precision", 0),
        recall=aggregated_metrics.get("Recall", 0),
        human_ai_agreement_rate=aggregated_metrics.get("Human Ai Agreement Rate", 0),
        time_to_resolution=aggregated_metrics.get("Time To Resolution", 0),
        human_effort_saved=aggregated_metrics.get("Human Effort Saved", 0),
        ai_assistance_rate=aggregated_metrics.get("Ai Assistance Rate", 0),
        learning_efficiency=aggregated_metrics.get("Learning Efficiency", 0),
        correction_efficiency=aggregated_metrics.get("Correction Efficiency", 0),
        evaluation_date=datetime.datetime.utcnow()
    )

    db.add(result)
    db.commit()

    return result
