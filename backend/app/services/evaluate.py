import datetime
import io
import json
import os
from dotenv import load_dotenv
from minio import Minio, S3Error
from sqlmodel import Session
from app.services.metrics import Metrics
from app.models import EvaluationConfig, LogEntry
from app.services.agg_metrics import calculate_metrics_for_group, save_evaluation_result
from app.models.results import EvaluationResult
from app.utils.database import SessionLocal


load_dotenv()

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
    region=os.getenv("MINIO_REGION"),
)


def evaluate_logs(config: EvaluationConfig, logs_data: list):
    # Aggregating interaction data across all sessions
    all_interaction_data = []
    for session in logs_data:
        interaction_data = session.get("interaction_data", {})
        all_interaction_data.append(interaction_data)

    # Calculating metrics based on aggregated interaction data
    metrics_results = {}

    for metric_name in config.metrics:
        if metric_name == "Prediction Accuracy":
            metrics_results["prediction_accuracy"] = Metrics.Performance.calculate_prediction_accuracy(all_interaction_data)
        elif metric_name == "Response Time":
            metrics_results["response_time"] = Metrics.Efficiency.calculate_response_time(all_interaction_data)
        elif metric_name == "Teaching Efficiency":
            metrics_results["teaching_efficiency"] = Metrics.Efficiency.calculate_teaching_efficiency(all_interaction_data)
        elif metric_name == "Overall System Accuracy":
            metrics_results["overall_system_accuracy"] = Metrics.Performance.calculate_overall_system_accuracy(all_interaction_data)
        elif metric_name == "Objective Fulfillment Rate":
            metrics_results["objective_fulfillment_rate"] = Metrics.AdaptabilityAndLearning.calculate_objective_fulfillment_rate(all_interaction_data)
        elif metric_name == "Feedback Impact":
            metrics_results["feedback_impact"] = Metrics.AdaptabilityAndLearning.calculate_feedback_impact(all_interaction_data)
        elif metric_name == "Adaptability Score":
            metrics_results["adaptability_score"] = Metrics.AdaptabilityAndLearning.calculate_adaptability_score(all_interaction_data)
        elif metric_name == "Query Efficiency":
            metrics_results["query_efficiency"] = Metrics.Efficiency.calculate_query_efficiency(all_interaction_data)
        elif metric_name == "Error Reduction Rate":
            metrics_results["error_reduction_rate"] = Metrics.Efficiency.calculate_error_reduction_rate(all_interaction_data)
        elif metric_name == "Confidence":
            metrics_results["confidence"] = Metrics.TrustAndSafety.calculate_confidence(all_interaction_data)
        elif metric_name == "Model Improvement Rate":
            metrics_results["ai_model_improvement_rate"] = Metrics.Performance.calculate_model_improvement_rate(all_interaction_data)
        elif metric_name == "Resource Utilization":
            metrics_results["resource_utilization"] = Metrics.Efficiency.calculate_resource_utilization(all_interaction_data)
        elif metric_name == "Impact of Corrections":
            metrics_results["impact_of_corrections"] = Metrics.AdaptabilityAndLearning.calculate_impact_of_corrections(all_interaction_data)
        elif metric_name == "Decision Effectiveness":
            metrics_results["decision_effectiveness"] = Metrics.CollaborationAndInteraction.calculate_decision_effectiveness(all_interaction_data)
        elif metric_name == "Knowledge Retention":
            metrics_results["knowledge_retention"] = Metrics.Efficiency.calculate_knowledge_retention(all_interaction_data)
        elif metric_name == "Task Completion Time":
            metrics_results["task_completion_time"] = Metrics.Efficiency.calculate_task_completion_time(all_interaction_data)
        elif metric_name == "Trust Score":
            metrics_results["trust_score"] = Metrics.TrustAndSafety.calculate_trust_score(all_interaction_data)
        elif metric_name == "Safety Incidents":
            metrics_results["safety_incidents"] = Metrics.TrustAndSafety.calculate_safety_incidents(all_interaction_data)
        elif metric_name == "Adversarial Robustness":
            metrics_results["adversarial_robustness"] = Metrics.RobustnessAndGeneralization.calculate_adversarial_robustness(all_interaction_data)
        elif metric_name == "Domain Generalization":
            metrics_results["domain_generalization"] = Metrics.RobustnessAndGeneralization.calculate_domain_generalization(all_interaction_data)
        elif metric_name == "System Reliability":
            metrics_results["system_reliability"] = Metrics.TrustAndSafety.calculate_system_reliability(all_interaction_data)
        elif metric_name == "Precision":
            metrics_results["precision"] = Metrics.Performance.calculate_precision(all_interaction_data)
        elif metric_name == "Recall":
            metrics_results["recall"] = Metrics.Performance.calculate_recall(all_interaction_data)
        elif metric_name == "Human-AI Agreement Rate":
            metrics_results["human_ai_agreement_rate"] = Metrics.CollaborationAndInteraction.calculate_human_ai_agreement_rate(all_interaction_data)
        elif metric_name == "Time to Resolution":
            metrics_results["time_to_resolution"] = Metrics.CollaborationAndInteraction.calculate_time_to_resolution(all_interaction_data)
        elif metric_name == "Human Effort Saved":
            metrics_results["human_effort_saved"] = Metrics.CollaborationAndInteraction.calculate_human_effort_saved(all_interaction_data)
        elif metric_name == "AI Assistance Rate":
            metrics_results["ai_assistance_rate"] = Metrics.CollaborationAndInteraction.calculate_ai_assistance_rate(all_interaction_data)
        elif metric_name == "Learning Efficiency":
            metrics_results["learning_efficiency"] = Metrics.AdaptabilityAndLearning.calculate_learning_efficiency(all_interaction_data)
        elif metric_name == "Correction Efficiency":
            metrics_results["correction_efficiency"] = Metrics.Efficiency.calculate_correction_efficiency(all_interaction_data)

    return metrics_results




def run_evaluation(config_id: int):
    # Create a new session for the background task
    new_session = SessionLocal()

    try:
        # Re-fetch the configuration within the new session using the configuration ID
        config = new_session.query(EvaluationConfig).get(config_id)
        if not config:
            raise ValueError("Configuration not found")

        # Use the `minio_path` from the database to fetch the configuration file
        config_minio_path = config.minio_path  # Assuming `minio_path` is stored correctly in the DB
        if not config_minio_path:
            raise ValueError("MinIO path for configuration not found in the database for this configuration")

        # Fetch the configuration file from MinIO
        try:
            config_file_object = minio_client.get_object(os.getenv("MINIO_BUCKET"), config_minio_path)
            config_data = json.load(io.BytesIO(config_file_object.read()))
        except S3Error as e:
            raise ValueError(f"Error fetching configuration file from MinIO: {str(e)}")

        # # Ensure that config_data contains the necessary information
        # if not isinstance(config_data, dict):
        #     raise ValueError("Invalid configuration format")

        # Fetch the associated logs path from the `log_minio_path` field in the database
        minio_path = config.minio_path  # Assuming there's a `log_minio_path` field in the DB
        if not minio_path:
            raise ValueError("MinIO path for logs not found in the database for this configuration")

        # Fetch the logs file from MinIO
        try:
            logs_file_object = minio_client.get_object(os.getenv("MINIO_BUCKET"), minio_path)
            logs_data = json.load(io.BytesIO(logs_file_object.read()))
        except S3Error as e:
            raise ValueError(f"Error fetching logs file from MinIO: {str(e)}")

        if not isinstance(logs_data, list):
            raise ValueError("Invalid logs format. Expected a list of log entries.")

        # Run the evaluation using the fetched configuration and logs
        results = evaluate_logs(config, logs_data)

        # Initialize the EvaluationResult with all calculated metrics
        db_result = EvaluationResult(
            configuration_id=config.id,
            evaluation_date=datetime.datetime.utcnow(),
            **results  # Unpack the results dictionary to match column names in the EvaluationResult model
        )

        # Add and commit the single instance with all metrics
        new_session.add(db_result)
        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED
    except Exception as e:
        # Update the status to failed if there was an error
        config.evaluation_status = EvaluationConfig.STATUS_FAILED
        print(f"Error during evaluation: {e}")
    finally:
        new_session.commit()
        new_session.close()  # Close the session when done




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
    aggregated_metrics = calculate_metrics_for_group(logs)

    # Save evaluation results
    save_evaluation_result(db, configuration_id, aggregated_metrics)

    return aggregated_metrics