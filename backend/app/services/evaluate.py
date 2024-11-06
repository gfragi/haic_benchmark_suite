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

    # Initialize sets to track unique versions
    unique_app_versions = set()
    unique_ai_model_versions = set()

    # Aggregating interaction data across all sessions
    all_interaction_data = []
    for session in logs_data:
        interaction_data = session.get("interaction_data", {})
        all_interaction_data.append(interaction_data)

    # Iterate through logs to collect versions and compute metrics
    for entry in logs_data:
        # Collect the app version and AI model version from the main entry
        app_version = entry.get('app_version', "Unknown")
        ai_model_version = entry.get('ai_model_version', "Unknown")
        unique_app_versions.add(app_version)
        unique_ai_model_versions.add(ai_model_version)

        # Check retrain events and collect AI model versions after retraining
        # if 'retrain_events' in entry:
        #     for event in entry['retrain_events']:
        #         retrained_version = event.get('retraining_details', {}).get('ai_model_version_after_retraining')
        #         if retrained_version:
        #             unique_ai_model_versions.add(retrained_version)

    # Initialize the dictionary to hold metrics grouped by metric group
    metrics_results_by_group = {}

    # Fetch metric groups from the database
    metric_groups = db.query(MetricGroup).all()

    # Loop through each metric group and calculate metrics for each group
    for group in metric_groups:
        group_results = {}

        for metric in group.metrics:
            if metric.name == "Prediction Accuracy":
                group_results["Prediction Accuracy"] = Metrics.Effectiveness.calculate_prediction_accuracy(all_interaction_data)
            elif metric.name == "Response Time":
                group_results["Response Time"] = Metrics.Efficiency.calculate_response_time(all_interaction_data)
            elif metric.name == "Teaching Efficiency":
                group_results["Teaching Efficiency"] = Metrics.Efficiency.calculate_teaching_efficiency(all_interaction_data)
            elif metric.name == "Overall System Accuracy":
                group_results["Overall System Accuracy"] = Metrics.Effectiveness.calculate_overall_system_accuracy(all_interaction_data)
            elif metric.name == "Objective Fulfillment Rate":
                group_results["Objective Fulfillment Rate"] = Metrics.AdaptabilityAndLearning.calculate_objective_fulfillment_rate(all_interaction_data)
            elif metric.name == "Feedback Impact":
                group_results["Feedback Impact"] = Metrics.AdaptabilityAndLearning.calculate_feedback_impact(all_interaction_data)
            elif metric.name == "Adaptability Score":
                group_results["Adaptability Score"] = Metrics.AdaptabilityAndLearning.calculate_adaptability_score(all_interaction_data)
            elif metric.name == "Query Efficiency":
                group_results["Query Efficiency"] = Metrics.Efficiency.calculate_query_efficiency(all_interaction_data)
            elif metric.name == "Error Reduction Rate":
                group_results["Error Reduction Rate"] = Metrics.Efficiency.calculate_error_reduction_rate(all_interaction_data)
            elif metric.name == "Confidence":
                group_results["Confidence"] = Metrics.TrustAndSafety.calculate_confidence(all_interaction_data)
            elif metric.name == "Model Improvement Rate":
                group_results["Model Improvement Rate"] = Metrics.Effectiveness.calculate_model_improvement_rate(all_interaction_data)
            elif metric.name == "Resource Utilization":
                group_results["Resource Utilization"] = Metrics.Efficiency.calculate_resource_utilization(all_interaction_data)
            elif metric.name == "Impact of Corrections":
                group_results["Impact of Corrections"] = Metrics.AdaptabilityAndLearning.calculate_impact_of_corrections(all_interaction_data)
            elif metric.name == "Decision Effectiveness":
                group_results["Decision Effectiveness"] = Metrics.CollaborationAndInteraction.calculate_decision_effectiveness(all_interaction_data)
            elif metric.name == "Knowledge Retention":
                group_results["Knowledge Retention"] = Metrics.Efficiency.calculate_knowledge_retention(all_interaction_data)
            elif metric.name == "Task Completion Time":
                group_results["Task Completion Time"] = Metrics.Efficiency.calculate_task_completion_time(all_interaction_data)
            elif metric.name == "Trust Score":
                group_results["Trust Score"] = Metrics.TrustAndSafety.calculate_trust_score(all_interaction_data)
            elif metric.name == "Safety Incidents":
                group_results["Safety Incidents"] = Metrics.TrustAndSafety.calculate_safety_incidents(all_interaction_data)
            elif metric.name == "Adversarial Robustness":
                group_results["Adversarial Robustness"] = Metrics.RobustnessAndGeneralization.calculate_adversarial_robustness(all_interaction_data)
            elif metric.name == "Domain Generalization":
                group_results["Domain Generalization"] = Metrics.RobustnessAndGeneralization.calculate_domain_generalization(all_interaction_data)
            elif metric.name == "System Reliability":
                group_results["System Reliability"] = Metrics.TrustAndSafety.calculate_system_reliability(all_interaction_data)
            elif metric.name == "Precision":
                group_results["Precision"] = Metrics.Effectiveness.calculate_precision(all_interaction_data)
            elif metric.name == "Recall":
                group_results["Recall"] = Metrics.Effectiveness.calculate_recall(all_interaction_data)
            elif metric.name == "Human-AI Agreement Rate":
                group_results["Human-AI Agreement Rate"] = Metrics.CollaborationAndInteraction.calculate_human_ai_agreement_rate(all_interaction_data)
            elif metric.name == "Time to Resolution":
                group_results["Time to Resolution"] = Metrics.CollaborationAndInteraction.calculate_time_to_resolution(all_interaction_data)
            elif metric.name == "Human Effort Saved":
                group_results["Human Effort Saved"] = Metrics.CollaborationAndInteraction.calculate_human_effort_saved(all_interaction_data)
            elif metric.name == "AI Assistance Rate":
                group_results["AI Assistance Rate"] = Metrics.CollaborationAndInteraction.calculate_ai_assistance_rate(all_interaction_data)
            elif metric.name == "Learning Efficiency":
                group_results["Learning Efficiency"] = Metrics.AdaptabilityAndLearning.calculate_learning_efficiency(all_interaction_data)
            elif metric.name == "Correction Efficiency":
                group_results["Correction Efficiency"] = Metrics.Efficiency.calculate_correction_efficiency(all_interaction_data)

        # Save the results of this group into the final results dictionary
        metrics_results_by_group[group.name] = group_results


    # Convert sets to lists for JSON serialization
    unique_app_versions = list(unique_app_versions)
    unique_ai_model_versions = list(unique_ai_model_versions)

    return metrics_results_by_group, unique_app_versions, unique_ai_model_versions



def split_logs_by_ai_model_version(logs_data: list):
    # Create a dictionary to hold logs by AI model version
    logs_by_ai_version = {}

    # Iterate through the logs and separate them by AI model version
    for entry in logs_data:
        ai_model_version = entry.get('ai_model_version', "Unknown")

        if ai_model_version not in logs_by_ai_version:
            logs_by_ai_version[ai_model_version] = []

        # Append the log entry to the corresponding version list
        logs_by_ai_version[ai_model_version].append(entry)

        # Also check for retrain events and track those versions
        # if 'retrain_events' in entry:
        #     for event in entry['retrain_events']:
        #         retrained_version = event.get('retraining_details', {}).get('ai_model_version_after_retraining')
        #         if retrained_version:
        #             if retrained_version not in logs_by_ai_version:
        #                 logs_by_ai_version[retrained_version] = []
        #             logs_by_ai_version[retrained_version].append(event)

    return logs_by_ai_version



def run_evaluation(config_id: int):
    new_session = SessionLocal()

    try:
        config = new_session.query(EvaluationConfig).get(config_id)
        if not config:
            raise ValueError("Configuration not found")

        # Fetch logs from MinIO (existing logic)
        logs_file_object = minio_client.get_object(os.getenv("MINIO_BUCKET"), config.minio_path)
        logs_data = json.load(io.BytesIO(logs_file_object.read()))

        # Split logs by AI model version
        logs_by_ai_version = split_logs_by_ai_model_version(logs_data)

        # Evaluate logs for each AI model version separately
        for ai_model_version, logs in logs_by_ai_version.items():
            print(f"Evaluating AI model version: {ai_model_version}")
            results_by_group, app_versions, _ = evaluate_logs(config, logs, new_session)

            # Join the app versions into a comma-separated string
            app_version_str = ', '.join(app_versions)

            result_data = {
                'configuration_id': config.id,
                'evaluation_date': str(datetime.datetime.utcnow()),
                'app_version': app_version_str,  # List of unique app versions
                'ai_model_version': ai_model_version,  # Single AI model version for this evaluation
                'metrics': results_by_group,
            }

            # Save results to MinIO
            result_file_path = f"{config.id}/results/{uuid.uuid4()}.json"
            result_json = json.dumps(result_data)
            minio_client.put_object(
                bucket_name=os.getenv("MINIO_BUCKET"),
                object_name=result_file_path,
                data=io.BytesIO(result_json.encode('utf-8')),
                length=len(result_json)
            )

            # Save EvaluationResult with the current AI model version
            db_result = EvaluationResult(
                configuration_id=config.id,
                evaluation_date=datetime.datetime.utcnow(),
                result_minio_path=result_file_path,
                app_version=app_version_str,  # Store app versions as a comma-separated string
                ai_model_version=ai_model_version  # Single AI model version for this evaluation
            )
            new_session.add(db_result)
            new_session.commit()

        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED

    except Exception as e:
        config.evaluation_status = EvaluationConfig.STATUS_FAILED
        print(f"Error during evaluation: {e}")
    finally:
        new_session.commit()
        new_session.close()
