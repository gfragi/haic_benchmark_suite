import datetime
import io
import json
import os
import uuid
from dotenv import load_dotenv
from minio import Minio, S3Error
from sqlmodel import Session
from app.services.metrics import Metrics
from app.models import EvaluationConfig, LogEntry
from app.services.agg_metrics import calculate_metrics_for_group, save_evaluation_result
from app.models.results import EvaluationResult, MetricGroup
from app.utils.database import SessionLocal


load_dotenv()

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
    region=os.getenv("MINIO_REGION"),
)


def evaluate_logs(config: EvaluationConfig, logs_data: list, db: Session):
    # Aggregating interaction data across all sessions
    all_interaction_data = []
    for session in logs_data:
        interaction_data = session.get("interaction_data", {})
        all_interaction_data.append(interaction_data)

    # Initialize the dictionary to hold metrics grouped by metric group
    metrics_results_by_group = {}

    # Fetch metric groups from the database
    metric_groups = db.query(MetricGroup).all()

    # Loop through each metric group and calculate metrics for each group
    for group in metric_groups:
        group_results = {}

        for metric in group.metrics:
            if metric.name == "Prediction Accuracy":
                group_results["prediction_accuracy"] = Metrics.Performance.calculate_prediction_accuracy(all_interaction_data)
            elif metric.name == "Response Time":
                group_results["response_time"] = Metrics.Efficiency.calculate_response_time(all_interaction_data)
            elif metric.name == "Teaching Efficiency":
                group_results["teaching_efficiency"] = Metrics.Efficiency.calculate_teaching_efficiency(all_interaction_data)
            elif metric.name == "Overall System Accuracy":
                group_results["overall_system_accuracy"] = Metrics.Performance.calculate_overall_system_accuracy(all_interaction_data)
            elif metric.name == "Objective Fulfillment Rate":
                group_results["objective_fulfillment_rate"] = Metrics.AdaptabilityAndLearning.calculate_objective_fulfillment_rate(all_interaction_data)
            elif metric.name == "Feedback Impact":
                group_results["feedback_impact"] = Metrics.AdaptabilityAndLearning.calculate_feedback_impact(all_interaction_data)
            elif metric.name == "Adaptability Score":
                group_results["adaptability_score"] = Metrics.AdaptabilityAndLearning.calculate_adaptability_score(all_interaction_data)
            elif metric.name == "Query Efficiency":
                group_results["query_efficiency"] = Metrics.Efficiency.calculate_query_efficiency(all_interaction_data)
            elif metric.name == "Error Reduction Rate":
                group_results["error_reduction_rate"] = Metrics.Efficiency.calculate_error_reduction_rate(all_interaction_data)
            elif metric.name == "Confidence":
                group_results["confidence"] = Metrics.TrustAndSafety.calculate_confidence(all_interaction_data)
            elif metric.name == "Model Improvement Rate":
                group_results["ai_model_improvement_rate"] = Metrics.Performance.calculate_model_improvement_rate(all_interaction_data)
            elif metric.name == "Resource Utilization":
                group_results["resource_utilization"] = Metrics.Efficiency.calculate_resource_utilization(all_interaction_data)
            elif metric.name == "Impact of Corrections":
                group_results["impact_of_corrections"] = Metrics.AdaptabilityAndLearning.calculate_impact_of_corrections(all_interaction_data)
            elif metric.name == "Decision Effectiveness":
                group_results["decision_effectiveness"] = Metrics.CollaborationAndInteraction.calculate_decision_effectiveness(all_interaction_data)
            elif metric.name == "Knowledge Retention":
                group_results["knowledge_retention"] = Metrics.Efficiency.calculate_knowledge_retention(all_interaction_data)
            elif metric.name == "Task Completion Time":
                group_results["task_completion_time"] = Metrics.Efficiency.calculate_task_completion_time(all_interaction_data)
            elif metric.name == "Trust Score":
                group_results["trust_score"] = Metrics.TrustAndSafety.calculate_trust_score(all_interaction_data)
            elif metric.name == "Safety Incidents":
                group_results["safety_incidents"] = Metrics.TrustAndSafety.calculate_safety_incidents(all_interaction_data)
            elif metric.name == "Adversarial Robustness":
                group_results["adversarial_robustness"] = Metrics.RobustnessAndGeneralization.calculate_adversarial_robustness(all_interaction_data)
            elif metric.name == "Domain Generalization":
                group_results["domain_generalization"] = Metrics.RobustnessAndGeneralization.calculate_domain_generalization(all_interaction_data)
            elif metric.name == "System Reliability":
                group_results["system_reliability"] = Metrics.TrustAndSafety.calculate_system_reliability(all_interaction_data)
            elif metric.name == "Precision":
                group_results["precision"] = Metrics.Performance.calculate_precision(all_interaction_data)
            elif metric.name == "Recall":
                group_results["recall"] = Metrics.Performance.calculate_recall(all_interaction_data)
            elif metric.name == "Human-AI Agreement Rate":
                group_results["human_ai_agreement_rate"] = Metrics.CollaborationAndInteraction.calculate_human_ai_agreement_rate(all_interaction_data)
            elif metric.name == "Time to Resolution":
                group_results["time_to_resolution"] = Metrics.CollaborationAndInteraction.calculate_time_to_resolution(all_interaction_data)
            elif metric.name == "Human Effort Saved":
                group_results["human_effort_saved"] = Metrics.CollaborationAndInteraction.calculate_human_effort_saved(all_interaction_data)
            elif metric.name == "AI Assistance Rate":
                group_results["ai_assistance_rate"] = Metrics.CollaborationAndInteraction.calculate_ai_assistance_rate(all_interaction_data)
            elif metric.name == "Learning Efficiency":
                group_results["learning_efficiency"] = Metrics.AdaptabilityAndLearning.calculate_learning_efficiency(all_interaction_data)
            elif metric.name == "Correction Efficiency":
                group_results["correction_efficiency"] = Metrics.Efficiency.calculate_correction_efficiency(all_interaction_data)

        # Save the results of this group into the final results dictionary
        metrics_results_by_group[group.name] = group_results

    return metrics_results_by_group




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

        # Fetch the associated logs path from the `minio_path` field in the database
        minio_path = config.minio_path  # Assuming there's a `minio_path` field in the DB
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

        # Pass the db session (new_session) to the evaluate_logs function
        results_by_group = evaluate_logs(config, logs_data, new_session)

        # Prepare the result data
        result_data = {
            'configuration_id': config.id,
            'evaluation_date': str(datetime.datetime.utcnow()),
            'metrics': results_by_group  # Save grouped results
        }

        # Store the evaluation result in MinIO under `config_id/results/result_id.json`
        result_file_path = f"{config.id}/results/{uuid.uuid4()}.json"
        result_json = json.dumps(result_data)

        minio_client.put_object(
            bucket_name=os.getenv("MINIO_BUCKET"),
            object_name=result_file_path,
            data=io.BytesIO(result_json.encode('utf-8')),
            length=len(result_json)
        )

        # Create a new EvaluationResult and save the MinIO path
        db_result = EvaluationResult(
            configuration_id=config.id,
            evaluation_date=datetime.datetime.utcnow(),
            result_minio_path=result_file_path  # Store the path of the results
        )

        # Add the EvaluationResult to the session and commit
        new_session.add(db_result)
        new_session.commit()

        # Mark evaluation as complete
        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED

    except Exception as e:
        # Update the status to failed if there was an error
        config.evaluation_status = EvaluationConfig.STATUS_FAILED
        print(f"Error during evaluation: {e}")
    finally:
        new_session.commit()
        new_session.close()  # Close the session when done
