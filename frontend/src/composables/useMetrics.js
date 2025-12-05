// Composable for metrics data and logic
import { ref } from 'vue'

export function useMetrics() {
  const metricGroups = ref([
    {
      title: "Effectiveness Metrics",
      icon: "mdi-chart-line",
      iconColor: "success",
      metrics: [
        {
          title: "Prediction Accuracy",
          description: "Measures how accurately the AI predicts outcomes based on true positives and true negatives.",
          formula: "Accuracy = (True Positives + True Negatives) / Total Predictions"
        },
        {
          title: "Precision",
          description: "Indicates the proportion of true positive predictions out of all positive predictions made by the AI.",
          formula: "Precision = True Positives / (True Positives + False Positives)"
        },
        {
          title: "Recall",
          description: "Reflects the proportion of true positives identified out of all actual positives.",
          formula: "Recall = True Positives / (True Positives + False Negatives)"
        },
        {
          title: "Overall System Accuracy",
          description: "Percentage of correct outcomes produced by the system.",
          formula: "Overall System Accuracy = (Number of Correct Outcomes / Total Number of Outcomes) * 100"
        },
        {
          title: "Model Improvement Rate",
          description: "The rate at which the AI model improves its performance over a given time period.",
          formula: "Model Improvement Rate = (Performance at Time T - Performance at Time T-1) / Time Interval"
        }
      ]
    },
    {
      title: "Efficiency Metrics",
      icon: "mdi-timer-sand",
      iconColor: "warning",
      metrics: [
        {
          title: "Response Time",
          description: "Average time taken by the AI to respond to queries.",
          formula: "Response Time = Total Response Time / Number of Queries"
        },
        {
          title: "Task Completion Time",
          description: "Time saved by using AI compared to completing the task without AI.",
          formula: "Task Completion Time = Time Without AI - Time With AI"
        },
        {
          title: "Teaching Efficiency",
          description: "Efficiency of performance improvement relative to the time spent teaching the AI.",
          formula: "Teaching Efficiency = Performance Improvement / Time Spent"
        },
        {
          title: "Query Efficiency",
          description: "Number of queries needed to reach a target accuracy.",
          formula: "Query Efficiency = Total Queries / Queries to Reach Target"
        },
        {
          title: "Resource Utilization",
          description: "The percentage of resources used by the AI relative to the total available resources.",
          formula: "Resource Utilization = (Resources Used / Total Resources Available) * 100"
        }
      ]
    },
    {
      title: "Adaptability and Learning Metrics",
      icon: "mdi-lightbulb-on-outline",
      iconColor: "info",
      metrics: [
        {
          title: "Feedback Impact",
          description: "Improvement in AI performance after receiving human feedback.",
          formula: "Feedback Impact = Performance Post-Feedback - Performance Pre-Feedback"
        },
        {
          title: "Adaptability Score",
          description: "AI's ability to adapt and improve after receiving feedback or adjustments.",
          formula: "Adaptability Score = Performance Post-Adaptation - Performance Pre-Adaptation"
        },
        {
          title: "Impact of Corrections",
          description: "Improvement in system performance following human corrections.",
          formula: "Impact of Corrections = Performance Post-Correction - Performance Pre-Correction"
        },
        {
          title: "Learning Efficiency",
          description: "The efficiency of human learning when assisted by AI.",
          formula: "Learning Efficiency = Learning Gains / Time Spent Learning"
        }
      ]
    },
    {
      title: "Collaboration and Interaction Metrics",
      icon: "mdi-account-group",
      iconColor: "secondary",
      metrics: [
        {
          title: "Human-AI Agreement Rate",
          description: "The rate of agreement between human decisions and AI suggestions.",
          formula: "Human-AI Agreement Rate = Agreements / Total Decisions"
        },
        {
          title: "AI Assistance Rate",
          description: "The frequency with which AI assists in human decisions.",
          formula: "AI Assistance Rate = Assisted Decisions / Total Decisions"
        },
        {
          title: "Decision Effectiveness",
          description: "The effectiveness of decisions made with AI support, measured as a percentage of successful decisions.",
          formula: "Decision Effectiveness = (Successful Decisions / Total Decisions) * 100"
        }
      ]
    },
    {
      title: "Trust and Safety Metrics",
      icon: "mdi-shield-check-outline",
      iconColor: "success",
      metrics: [
        {
          title: "Confidence",
          description: "Percentage of high-confidence correct predictions made by the AI.",
          formula: "Confidence = (Correct High Confidence Predictions / Total High Confidence Predictions) * 100"
        },
        {
          title: "Trust Score",
          description: "Level of trust users place in the AI system, measured as a percentage.",
          formula: "Trust Score = (Total Trust Ratings / Total Trust Scale) * 100"
        },
        {
          title: "Safety Incidents",
          description: "The number of safety-related incidents reported during AI operation.",
          formula: "Safety Incidents = Sum of Safety Incidents"
        }
      ]
    },
    {
      title: "Robustness and Generalization Metrics",
      icon: "mdi-shield-alert-outline",
      iconColor: "error",
      metrics: [
        {
          title: "Adversarial Robustness",
          description: "AI performance in adversarial conditions compared to normal conditions.",
          formula: "Adversarial Robustness = Performance Adversarial / Performance Normal"
        },
        {
          title: "Domain Generalization",
          description: "The AI's ability to generalize its performance across different domains relative to a baseline.",
          formula: "Domain Generalization = Performance Across Domains / Baseline Performance"
        }
      ]
    }
  ])

  return {
    metricGroups,
  }
}
