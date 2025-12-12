function useMetrics() {
  return {
    metricGroups: {
      value: [
        {
          title: "Effectiveness Metrics",
          icon: "mdi-chart-line",
          iconColor: "success",
          metrics: [
            {
              title: "Prediction Accuracy",
              description: "Accuracy of predictions",
              formula: "TP + TN / Total Predictions",
            },
            {
              title: "Precision",
              description: "Precision metric",
              formula: "TP / (TP + FP)",
            },
            {
              title: "Recall",
              description: "Recall metric",
              formula: "TP / (TP + FN)",
            },
            {
              title: "Overall System Accuracy",
              description: "Overall accuracy",
              formula: "Correct Predictions / Total Predictions",
            },
            {
              title: "Model Improvement Rate",
              description: "Improvement rate",
              formula: "(New Accuracy - Old Accuracy) / Old Accuracy",
            },
          ],
        },
        {
          title: "Efficiency Metrics",
          icon: "mdi-timer-sand",
          iconColor: "warning",
          metrics: [
            {
              title: "Response Time",
              description: "Average response time",
              formula: "Total Response Time / Number of Queries",
            },
            {
              title: "Task Completion Time",
              description: "Time to complete tasks",
              formula: "End Time - Start Time",
            },
            {
              title: "Teaching Efficiency",
              description: "Efficiency of teaching",
              formula: "Learned Concepts / Teaching Time",
            },
            {
              title: "Query Efficiency",
              description: "Efficiency of queries",
              formula: "Relevant Results / Total Results",
            },
            {
              title: "Resource Utilization",
              description: "Resource usage",
              formula: "Used Resources / Available Resources",
            },
          ],
        },
        {
          title: "Adaptability and Learning Metrics",
          icon: "mdi-lightbulb-on-outline",
          iconColor: "info",
          metrics: [
            {
              title: "Feedback Impact",
              description: "Impact of feedback",
              formula:
                "Performance After Feedback - Performance Before Feedback",
            },
            {
              title: "Adaptability Score",
              description: "Adaptability measurement",
              formula: "Successful Adaptations / Total Adaptation Attempts",
            },
            {
              title: "Impact of Corrections",
              description: "Effect of corrections",
              formula: "Accuracy After Correction - Accuracy Before Correction",
            },
            {
              title: "Learning Efficiency",
              description: "Learning efficiency",
              formula: "Knowledge Gained / Time Spent Learning",
            },
          ],
        },
        {
          title: "Collaboration and Interaction Metrics",
          icon: "mdi-account-group",
          iconColor: "secondary",
          metrics: [
            {
              title: "Human-AI Agreement Rate",
              description: "Rate of agreement",
              formula: "Agreed Decisions / Total Decisions",
            },
            {
              title: "AI Assistance Rate",
              description: "Rate of assistance",
              formula: "Assisted Tasks / Total Tasks",
            },
            {
              title: "Decision Effectiveness",
              description: "Effectiveness of decisions",
              formula: "Successful Outcomes / Total Decisions",
            },
          ],
        },
        {
          title: "Trust and Safety Metrics",
          icon: "mdi-shield-check-outline",
          iconColor: "success",
          metrics: [
            {
              title: "Confidence",
              description: "Confidence level",
              formula: "Confidence Score / Max Possible Score",
            },
            {
              title: "Trust Score",
              description: "Trust measurement",
              formula: "Trust Indicators / Total Indicators",
            },
            {
              title: "Safety Incidents",
              description: "Number of safety incidents",
              formula: "Incidents Count",
            },
          ],
        },
        {
          title: "Robustness and Generalization Metrics",
          icon: "mdi-shield-alert-outline",
          iconColor: "error",
          metrics: [
            {
              title: "Adversarial Robustness",
              description: "Resistance to adversarial inputs",
              formula: "Successful Defenses / Total Attacks",
            },
            {
              title: "Domain Generalization",
              description: "Generalization across domains",
              formula: "Cross-Domain Performance / Single-Domain Performance",
            },
          ],
        },
      ],
    },
  };
}

module.exports = { useMetrics };
