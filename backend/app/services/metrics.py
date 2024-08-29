class Metrics:
    class Performance:
        @staticmethod
        def calculate_prediction_accuracy(interaction_data):
            tp = sum(1 for item in interaction_data if item.get("result") == "true_positive")
            tn = sum(1 for item in interaction_data if item.get("result") == "true_negative")
            total = len(interaction_data)
            return (tp + tn) / total if total > 0 else 0

        @staticmethod
        def calculate_precision(interaction_data):
            tp = sum(1 for item in interaction_data if item.get("ai_detection_results") == "true_positive")
            fp = sum(1 for item in interaction_data if item.get("ai_detection_results") == "false_positive")
            return tp / (tp + fp) if (tp + fp) > 0 else 0

        @staticmethod
        def calculate_recall(interaction_data):
            tp = sum(1 for item in interaction_data if item.get("ai_detection_results") == "true_positive")
            fn = sum(1 for item in interaction_data if item.get("ai_detection_results") == "false_negative")
            return tp / (tp + fn) if (tp + fn) > 0 else 0

        @staticmethod
        def calculate_overall_system_accuracy(interaction_data):
            correct_outcomes = sum(1 for item in interaction_data if item.get("outcome") == "correct")
            total_outcomes = len(interaction_data)
            return (correct_outcomes / total_outcomes) * 100 if total_outcomes > 0 else 0

        @staticmethod
        def calculate_model_improvement_rate(interaction_data):
            performance_t = sum(item.get("performance_at_t", 0) for item in interaction_data)
            performance_t_1 = sum(item.get("performance_at_t_1", 0) for item in interaction_data)
            time_interval = sum(item.get("time_interval", 0) for item in interaction_data)
            return (performance_t - performance_t_1) / time_interval if time_interval > 0 else 0
        


    class Efficiency:
        @staticmethod
        def calculate_response_time(interaction_data):
            total_time = sum(item.get("response_time", 0) for item in interaction_data)
            num_queries = len(interaction_data)
            return total_time / num_queries if num_queries > 0 else 0

        @staticmethod
        def calculate_teaching_efficiency(interaction_data):
            performance_improvement = sum(item.get("performance_improvement", 0) for item in interaction_data)
            time_spent = sum(item.get("time_spent", 0) for item in interaction_data)
            return performance_improvement / time_spent if time_spent > 0 else 0

        @staticmethod
        def calculate_query_efficiency(interaction_data):
            total_queries = len(interaction_data)
            queries_to_target_accuracy = sum(1 for item in interaction_data if item.get("reached_target_accuracy", False))
            return total_queries / queries_to_target_accuracy if queries_to_target_accuracy > 0 else 0

        @staticmethod
        def calculate_resource_utilization(interaction_data):
            resources_used = sum(item.get("resources_used", 0) for item in interaction_data)
            total_resources = sum(item.get("total_resources", 0) for item in interaction_data)
            return (resources_used / total_resources) * 100 if total_resources > 0 else 0

        @staticmethod
        def calculate_task_completion_time(interaction_data):
            time_without_ai = sum(item.get("time_without_ai", 0) for item in interaction_data)
            time_with_ai = sum(item.get("time_with_ai", 0) for item in interaction_data)
            return time_without_ai - time_with_ai

        @staticmethod
        def calculate_correction_efficiency(interaction_data):
            """
            Calculates how efficiently corrections are made with AI support.
            """
            correction_effectiveness = sum(item.get("correction_effectiveness", 0) for item in interaction_data)
            time_spent_correcting = sum(item.get("correction_time", 0) for item in interaction_data)
            return correction_effectiveness / time_spent_correcting if time_spent_correcting > 0 else 0

        @staticmethod
        def calculate_error_reduction_rate(interaction_data):
            errors_before = sum(item.get("errors_before", 0) for item in interaction_data)
            errors_after = sum(item.get("errors_after", 0) for item in interaction_data)
            return ((errors_before - errors_after) / errors_before) * 100 if errors_before > 0 else 0


        @staticmethod
        def calculate_knowledge_retention(interaction_data):
            pre_retention_performance = sum(item.get("pre_retention_performance", 0) for item in interaction_data)
            post_retention_performance = sum(item.get("post_retention_performance", 0) for item in interaction_data)
            return (post_retention_performance / pre_retention_performance) * 100 if pre_retention_performance > 0 else 0

    class AdaptabilityAndLearning:
        @staticmethod
        def calculate_feedback_impact(interaction_data):
            pre_feedback_performance = sum(item.get("pre_feedback_performance", 0) for item in interaction_data)
            post_feedback_performance = sum(item.get("post_feedback_performance", 0) for item in interaction_data)
            return post_feedback_performance - pre_feedback_performance

        @staticmethod
        def calculate_adaptability_score(interaction_data):
            pre_adaptation_performance = sum(item.get("pre_adaptation_performance", 0) for item in interaction_data)
            post_adaptation_performance = sum(item.get("post_adaptation_performance", 0) for item in interaction_data)
            return post_adaptation_performance - pre_adaptation_performance

        @staticmethod
        def calculate_impact_of_corrections(interaction_data):
            pre_correction_performance = sum(item.get("pre_correction_performance", 0) for item in interaction_data)
            post_correction_performance = sum(item.get("post_correction_performance", 0) for item in interaction_data)
            return post_correction_performance - pre_correction_performance

        @staticmethod
        def calculate_learning_efficiency(interaction_data):
            learning_gains = sum(item.get("learning_gain", 0) for item in interaction_data)
            time_spent_learning = sum(item.get("learning_time", 0) for item in interaction_data)
            return learning_gains / time_spent_learning if time_spent_learning > 0 else 0

        @staticmethod
        def calculate_objective_fulfillment_rate(interaction_data):
            achieved_objectives = sum(1 for item in interaction_data if item.get("objective_status") == "achieved")
            total_objectives = len(interaction_data)
            return achieved_objectives / total_objectives if total_objectives > 0 else 0
    class CollaborationAndInteraction:
        @staticmethod
        def calculate_human_ai_agreement_rate(interaction_data):
            agreements = sum(1 for item in interaction_data if item.get("human_decision") == item.get("ai_suggestion"))
            total_decisions = len(interaction_data)
            return agreements / total_decisions if total_decisions > 0 else 0

        @staticmethod
        def calculate_ai_assistance_rate(interaction_data):
            assisted_decisions = sum(1 for item in interaction_data if item.get("ai_assisted"))
            total_decisions = len(interaction_data)
            return assisted_decisions / total_decisions if total_decisions > 0 else 0

        @staticmethod
        def calculate_decision_effectiveness(interaction_data):
            successful_decisions = sum(1 for item in interaction_data if item.get("decision_outcome") == "successful")
            total_decisions = len(interaction_data)
            return (successful_decisions / total_decisions) * 100 if total_decisions > 0 else 0

        @staticmethod
        def calculate_time_to_resolution(interaction_data):
            total_time = sum(item.get("resolution_time", 0) for item in interaction_data)
            num_resolutions = len(interaction_data)
            return total_time / num_resolutions if num_resolutions > 0 else 0

        @staticmethod
        def calculate_human_effort_saved(interaction_data):
            effort_without_ai = sum(item.get("effort_without_ai", 0) for item in interaction_data)
            effort_with_ai = sum(item.get("effort_with_ai", 0) for item in interaction_data)
            return effort_without_ai - effort_with_ai

    class TrustAndSafety:
        @staticmethod
        def calculate_confidence(interaction_data):
            high_confidence_correct = sum(1 for item in interaction_data if item.get("confidence_level", 0) >= 0.9 and item.get("result") == "correct")
            high_confidence_total = sum(1 for item in interaction_data if item.get("confidence_level", 0) >= 0.9)
            return (high_confidence_correct / high_confidence_total) * 100 if high_confidence_total > 0 else 0

        @staticmethod
        def calculate_trust_score(interaction_data):
            total_trust_ratings = sum(item.get("trust_rating", 0) for item in interaction_data)
            total_trust_scale = sum(item.get("trust_scale_maximum", 0) for item in interaction_data)
            return (total_trust_ratings / total_trust_scale) * 100 if total_trust_scale > 0 else 0

        @staticmethod
        def calculate_safety_incidents(interaction_data):
            return sum(item.get("safety_incidents", 0) for item in interaction_data)

        @staticmethod
        def calculate_system_reliability(interaction_data):
            uptime = sum(item.get("uptime", 0) for item in interaction_data)
            total_time = sum(item.get("total_time", 0) for item in interaction_data)
            return (uptime / total_time) * 100 if total_time > 0 else 0

    class RobustnessAndGeneralization:
        @staticmethod
        def calculate_adversarial_robustness(interaction_data):
            performance_adversarial = sum(item.get("performance_adversarial", 0) for item in interaction_data)
            performance_normal = sum(item.get("performance_normal", 0) for item in interaction_data)
            return performance_adversarial / performance_normal if performance_normal > 0 else 0

        @staticmethod
        def calculate_domain_generalization(interaction_data):
            performance_different_domains = sum(item.get("performance_across_domains", 0) for item in interaction_data)
            baseline_performance = sum(item.get("baseline_performance", 0) for item in interaction_data)
            return performance_different_domains / baseline_performance if baseline_performance > 0 else 0

    @staticmethod
    def get_available_metrics():
        return {
            "Performance": [
                "Prediction Accuracy",
                "Precision",
                "Recall",
                "Overall System Accuracy",
                "Model Improvement Rate",
            ],
            "Efficiency": [
                "Response Time",
                "Teaching Efficiency",
                "Query Efficiency",
                "Resource Utilization",
                "Task Completion Time",
                "Correction Efficiency",
                "Error Reduction Rate",
                "Knowledge Retention",
            ],
            "Adaptability and Learning": [
                "Feedback Impact",
                "Adaptability Score",
                "Impact of Corrections",
                "Learning Efficiency",
                "Objective Fullfillemnt Rate",
            ],
            "Collaboration and Interaction": [
                "Human-AI Agreement Rate",
                "AI Assistance Rate",
                "Decision Effectiveness",
                "Time to Resolution",
                "Human Effort Saved",
            ],
            "Trust and Safety": [
                "Confidence",
                "Trust Score",
                "Safety Incidents",
                "System Reliability",
            ],
            "Robustness and Generalization": [
                "Adversarial Robustness",
                "Domain Generalization",
            ],
        }
