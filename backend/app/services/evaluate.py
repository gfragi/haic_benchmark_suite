import json
from sqlmodel import Session
from app.services.metrics import *
from app.models import LogEntry, EvaluationConfig
from app.services.agg_metrics import calculate_aggregated_metrics, save_evaluation_result

def evaluate_logs(config: EvaluationConfig, log: list[LogEntry]):
    metrics_results = {}

    for log in log:
        interaction_data = log.interaction_data

        # Check if interaction_data is not a list, wrap it in a list
        if not isinstance(interaction_data, list):
            interaction_data = [interaction_data]

        # Ensure interaction_data is a list of dictionaries
        if not isinstance(interaction_data, list) or not all(isinstance(item, dict) for item in interaction_data):
            raise ValueError("Expected interaction_data to be a list of dictionaries")




        for metric_name in config.metrics:

            if metric_name == "Prediction Accuracy":
                    metrics_results["prediction_accuracy"] = calculate_prediction_accuracy(interaction_data)
            elif metric_name == "Response Time":
                metrics_results["response_time"] = calculate_response_time(interaction_data)
            elif metric_name == "Teaching Efficiency":
                metrics_results["teaching_efficiency"] = calculate_teaching_efficiency(interaction_data)
            elif metric_name == "Overall System Accuracy":
                metrics_results["overall_system_accuracy"] = calculate_overall_system_accuracy(interaction_data)
            elif metric_name == "Objective Fulfillment Rate":
                metrics_results["objective_fulfillment_rate"] = calculate_objective_fulfillment_rate(interaction_data)
            elif metric_name == "Feedback Impact":
                metrics_results["feedback_impact"] = calculate_feedback_impact(interaction_data)
            elif metric_name == "Adaptability Score":
                metrics_results["adaptability_score"] = calculate_adaptability_score(interaction_data)
            elif metric_name == "Query Efficiency":
                metrics_results["query_efficiency"] = calculate_query_efficiency(interaction_data)
            elif metric_name == "Error Reduction Rate":
                metrics_results["error_reduction_rate"] = calculate_error_reduction_rate(interaction_data)
            elif metric_name == "Confidence":
                metrics_results["confidence"] = calculate_confidence(interaction_data)
            elif metric_name == "Model Improvement Rate":
                metrics_results["ai_model_improvement_rate"] = calculate_model_improvement_rate(interaction_data)
            elif metric_name == "Resource Utilization":
                metrics_results["resource_utilization"] = calculate_resource_utilization(interaction_data)
            elif metric_name == "Impact of Corrections":
                metrics_results["impact_of_corrections"] = calculate_impact_of_corrections(interaction_data)
            elif metric_name == "Decision Effectiveness":
                metrics_results["decision_effectiveness"] = calculate_decision_effectiveness(interaction_data)
            elif metric_name == "Knowledge Retention":
                metrics_results["knowledge_retention"] = calculate_knowledge_retention(interaction_data)
            elif metric_name == "Task Completion Time":
                metrics_results["task_completion_time"] = calculate_task_completion_time(interaction_data)
            elif metric_name == "Trust Score":
                metrics_results["trust_score"] = calculate_trust_score(interaction_data)
            elif metric_name == "Safety Incidents":
                metrics_results["safety_incidents"] = calculate_safety_incidents(interaction_data)
            elif metric_name == "Adversarial Robustness":
                metrics_results["adversarial_robustness"] = calculate_adversarial_robustness(interaction_data)
            elif metric_name == "Domain Generalization":
                metrics_results["domain_generalization"] = calculate_domain_generalization(interaction_data)
            elif metric_name == "System Reliability":
                metrics_results["system_reliability"] = calculate_system_reliability(interaction_data)
            elif metric_name == "Precision":
                metrics_results["precision"] = calculate_precision(interaction_data)
            elif metric_name == "Recall":
                metrics_results["recall"] = calculate_recall(interaction_data)
            elif metric_name == "Human-AI Agreement Rate":
                metrics_results["human_ai_agreement_rate"] = calculate_human_ai_agreement_rate(interaction_data)
            elif metric_name == "Time to Resolution":
                metrics_results["time_to_resolution"] = calculate_time_to_resolution(interaction_data)
            elif metric_name == "Human Effort Saved":
                metrics_results["human_effort_saved"] = calculate_human_effort_saved(interaction_data)
            elif metric_name == "AI Assistance Rate":
                metrics_results["ai_assistance_rate"] = calculate_ai_assistance_rate(interaction_data)
            elif metric_name == "Learning Efficiency":
                metrics_results["learning_efficiency"] = calculate_learning_efficiency(interaction_data)
            elif metric_name == "Correction Efficiency":
                metrics_results["correction_efficiency"] = calculate_correction_efficiency(interaction_data)


                    # Add additional metrics as needed

    return metrics_results


def evaluate_logs_and_save_results(configuration_id: int, db: Session):
    """
    Evaluate logs associated with a configuration and save the results.
    """
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()

    if not config:
        raise ValueError("Configuration not found")

    # Fetch related logs
    logs = db.query(LogEntry).filter(LogEntry.configuration_id == configuration_id).all()

    if not logs:
        raise ValueError("No logs found for this configuration")

    # Calculate metrics
    aggregated_metrics = calculate_aggregated_metrics(logs)

    # Save evaluation results
    save_evaluation_result(db, configuration_id, aggregated_metrics)

    return aggregated_metrics