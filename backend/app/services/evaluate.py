from app.models import LogEntry, EvaluationConfig

def evaluate_log(log: LogEntry, config: EvaluationConfig):
    metrics_results = {}

    for metric in config.metrics:
        if metric.metric_name == "Prediction Accuracy":
            metrics_results["Prediction Accuracy"] = calculate_prediction_accuracy(log.interaction_data)
        elif metric.metric_name == "Response Time":
            metrics_results["Response Time"] = calculate_response_time(log.interaction_data)
        elif metric.metric_name == "Teaching Efficiency":
            metrics_results["Teaching Efficiency"] = calculate_teaching_efficiency(log.interaction_data)
        elif metric.metric_name == "Overall System Accuracy":
            metrics_results["Overall System Accuracy"] = calculate_overall_system_accuracy(log.interaction_data)
        elif metric.metric_name == "Objective Fulfillment Rate":
            metrics_results["Objective Fulfillment Rate"] = calculate_objective_fulfillment_rate(log.interaction_data)
        elif metric.metric_name == "Feedback Impact":
            metrics_results["Feedback Impact"] = calculate_feedback_impact(log.interaction_data)
        elif metric.metric_name == "Adaptability Score":
            metrics_results["Adaptability Score"] = calculate_adaptability_score(log.interaction_data)
        elif metric.metric_name == "Query Efficiency":
            metrics_results["Query Efficiency"] = calculate_query_efficiency(log.interaction_data)
        elif metric.metric_name == "Error Reduction Rate":
            metrics_results["Error Reduction Rate"] = calculate_error_reduction_rate(log.interaction_data)
        elif metric.metric_name == "Confidence":
            metrics_results["Confidence"] = calculate_confidence(log.interaction_data)
        elif metric.metric_name == "Model Improvement Rate":
            metrics_results["Model Improvement Rate"] = calculate_model_improvement_rate(log.interaction_data)
        elif metric.metric_name == "Resource Utilization":
            metrics_results["Resource Utilization"] = calculate_resource_utilization(log.interaction_data)
        elif metric.metric_name == "Impact of Corrections":
            metrics_results["Impact of Corrections"] = calculate_impact_of_corrections(log.interaction_data)
        elif metric.metric_name == "Decision Effectiveness":
            metrics_results["Decision Effectiveness"] = calculate_decision_effectiveness(log.interaction_data)
        elif metric.metric_name == "Knowledge Retention":
            metrics_results["Knowledge Retention"] = calculate_knowledge_retention(log.interaction_data)
        elif metric.metric_name == "Task Completion Time":
            metrics_results["Task Completion Time"] = calculate_task_completion_time(log.interaction_data)
        elif metric.metric_name == "Trust Score":
            metrics_results["Trust Score"] = calculate_trust_score(log.interaction_data)
        elif metric.metric_name == "Safety Incidents":
            metrics_results["Safety Incidents"] = calculate_safety_incidents(log.interaction_data)
        elif metric.metric_name == "Adversarial Robustness":
            metrics_results["Adversarial Robustness"] = calculate_adversarial_robustness(log.interaction_data)
        elif metric.metric_name == "Domain Generalization":
            metrics_results["Domain Generalization"] = calculate_domain_generalization(log.interaction_data)
        elif metric.metric_name == "System Reliability":
            metrics_results["System Reliability"] = calculate_system_reliability(log.interaction_data)
        # Add additional metrics as needed

    return metrics_results

def calculate_prediction_accuracy(interaction_data):
    tp = sum(1 for item in interaction_data if item.get("result") == "true_positive")
    tn = sum(1 for item in interaction_data if item.get("result") == "true_negative")
    total = len(interaction_data)
    return (tp + tn) / total if total > 0 else 0

def calculate_response_time(interaction_data):
    total_time = sum(item.get("response_time", 0) for item in interaction_data)
    num_queries = len(interaction_data)
    return total_time / num_queries if num_queries > 0 else 0

def calculate_teaching_efficiency(interaction_data):
    performance_improvement = sum(item.get("performance_improvement", 0) for item in interaction_data)
    time_spent = sum(item.get("time_spent", 0) for item in interaction_data)
    return performance_improvement / time_spent if time_spent > 0 else 0

def calculate_overall_system_accuracy(interaction_data):
    correct_outcomes = sum(1 for item in interaction_data if item.get("outcome") == "correct")
    total_outcomes = len(interaction_data)
    return (correct_outcomes / total_outcomes) * 100 if total_outcomes > 0 else 0

def calculate_objective_fulfillment_rate(interaction_data):
    achieved_objectives = sum(1 for item in interaction_data if item.get("objective_status") == "achieved")
    total_objectives = len(interaction_data)
    return achieved_objectives / total_objectives if total_objectives > 0 else 0

def calculate_feedback_impact(interaction_data):
    pre_feedback_performance = sum(item.get("pre_feedback_performance", 0) for item in interaction_data)
    post_feedback_performance = sum(item.get("post_feedback_performance", 0) for item in interaction_data)
    return post_feedback_performance - pre_feedback_performance

def calculate_adaptability_score(interaction_data):
    pre_adaptation_performance = sum(item.get("pre_adaptation_performance", 0) for item in interaction_data)
    post_adaptation_performance = sum(item.get("post_adaptation_performance", 0) for item in interaction_data)
    return post_adaptation_performance - pre_adaptation_performance


def calculate_query_efficiency(interaction_data):
    total_queries = len(interaction_data)
    queries_to_target_accuracy = sum(1 for item in interaction_data if item.get("reached_target_accuracy", False))
    return total_queries / queries_to_target_accuracy if queries_to_target_accuracy > 0 else 0


def calculate_error_reduction_rate(interaction_data):
    errors_before = sum(item.get("errors_before", 0) for item in interaction_data)
    errors_after = sum(item.get("errors_after", 0) for item in interaction_data)
    return ((errors_before - errors_after) / errors_before) * 100 if errors_before > 0 else 0


def calculate_confidence(interaction_data):
    high_confidence_correct = sum(1 for item in interaction_data if item.get("confidence_level") >= 0.9 and item.get("result") == "correct")
    high_confidence_total = sum(1 for item in interaction_data if item.get("confidence_level") >= 0.9)
    return (high_confidence_correct / high_confidence_total) * 100 if high_confidence_total > 0 else 0


def calculate_model_improvement_rate(interaction_data):
    performance_t = sum(item.get("performance_at_t", 0) for item in interaction_data)
    performance_t_1 = sum(item.get("performance_at_t_1", 0) for item in interaction_data)
    time_interval = sum(item.get("time_interval", 0) for item in interaction_data)
    return (performance_t - performance_t_1) / time_interval if time_interval > 0 else 0


def calculate_resource_utilization(interaction_data):
    resources_used = sum(item.get("resources_used", 0) for item in interaction_data)
    total_resources = sum(item.get("total_resources", 0) for item in interaction_data)
    return (resources_used / total_resources) * 100 if total_resources > 0 else 0


def calculate_impact_of_corrections(interaction_data):
    pre_correction_performance = sum(item.get("pre_correction_performance", 0) for item in interaction_data)
    post_correction_performance = sum(item.get("post_correction_performance", 0) for item in interaction_data)
    return post_correction_performance - pre_correction_performance


def calculate_decision_effectiveness(interaction_data):
    successful_decisions = sum(1 for item in interaction_data if item.get("decision_outcome") == "successful")
    total_decisions = len(interaction_data)
    return (successful_decisions / total_decisions) * 100 if total_decisions > 0 else 0


def calculate_knowledge_retention(interaction_data):
    pre_retention_performance = sum(item.get("pre_retention_performance", 0) for item in interaction_data)
    post_retention_performance = sum(item.get("post_retention_performance", 0) for item in interaction_data)
    return (post_retention_performance / pre_retention_performance) * 100 if pre_retention_performance > 0 else 0


def calculate_task_completion_time(interaction_data):
    time_without_ai = sum(item.get("time_without_ai", 0) for item in interaction_data)
    time_with_ai = sum(item.get("time_with_ai", 0) for item in interaction_data)
    return time_without_ai - time_with_ai


def calculate_trust_score(interaction_data):
    total_trust_ratings = sum(item.get("trust_rating", 0) for item in interaction_data)
    total_trust_scale = sum(item.get("trust_scale_maximum", 0) for item in interaction_data)
    return (total_trust_ratings / total_trust_scale) * 100 if total_trust_scale > 0 else 0


def calculate_safety_incidents(interaction_data):
    return sum(item.get("safety_incidents", 0) for item in interaction_data)


def calculate_adversarial_robustness(interaction_data):
    performance_adversarial = sum(item.get("performance_adversarial", 0) for item in interaction_data)
    performance_normal = sum(item.get("performance_normal", 0) for item in interaction_data)
    return performance_adversarial / performance_normal if performance_normal > 0 else 0


def calculate_domain_generalization(interaction_data):
    performance_different_domains = sum(item.get("performance_across_domains", 0) for item in interaction_data)
    baseline_performance = sum(item.get("baseline_performance", 0) for item in interaction_data)
    return performance_different_domains / baseline_performance if baseline_performance > 0 else 0


def calculate_system_reliability(interaction_data):
    uptime = sum(item.get("uptime", 0) for item in interaction_data)
    total_time = sum(item.get("total_time", 0) for item in interaction_data)
    return (uptime / total_time) * 100 if total_time > 0 else 0



# Add more metric calculation functions as needed
