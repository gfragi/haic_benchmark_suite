import apiClient from "./axios";

export default {
  getMetrics() {
    return apiClient.get("/evaluate/metrics");
  },
  runEvaluation(configuration_id) {
    return apiClient.post(`/evaluate/${configuration_id}`);
  },
  getResultDetail(configId, runId) {
    return apiClient.get(`/results/${configId}/${runId}`);
  },
};
