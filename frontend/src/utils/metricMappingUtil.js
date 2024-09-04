export function groupMetricsByCategory(result) {
  const metricMapping = {
    "Prediction Accuracy": "Performance",
    Precision: "Performance",
    Recall: "Performance",
    "Overall System Accuracy": "Performance",
    "Model Improvement Rate": "Performance",
    "Response Time": "Efficiency",
    "Teaching Efficiency": "Efficiency",
    "Query Efficiency": "Efficiency",
    "Resource Utilization": "Efficiency",
    "Task Completion Time": "Efficiency",
    "Correction Efficiency": "Efficiency",
    "Error Reduction Rate": "Efficiency",
    "Knowledge Retention": "Efficiency",
    "Feedback Impact": "Adaptability and Learning",
    "Adaptability Score": "Adaptability and Learning",
    "Impact Of Corrections": "Adaptability and Learning",
    "Learning Efficiency": "Adaptability and Learning",
    "Objective Fulfillment Rate": "Adaptability and Learning",
    "Human Ai Agreement Rate": "Collaboration and Interaction",
    "Ai Assistance Rate": "Collaboration and Interaction",
    "Decision Effectiveness": "Collaboration and Interaction",
    "Time To Resolution": "Collaboration and Interaction",
    "Human Effort Saved": "Collaboration and Interaction",
    Confidence: "Trust and Safety",
    "Trust Score": "Trust and Safety",
    "Safety Incidents": "Trust and Safety",
    "System Reliability": "Trust and Safety",
    "Adversarial Robustness": "Robustness and Generalization",
    "Domain Generalization": "Robustness and Generalization",
  };

  const groupedMetrics = {
    Performance: [],
    Efficiency: [],
    "Adaptability and Learning": [],
    "Collaboration and Interaction": [],
    "Trust and Safety": [],
    "Robustness and Generalization": [],
  };

  Object.keys(result).forEach((key) => {
    const group = metricMapping[key];
    if (group) {
      groupedMetrics[group].push({
        metric: key,
        value: result[key],
      });
    }
  });

  return groupedMetrics;
}
