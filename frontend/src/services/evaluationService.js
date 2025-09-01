import apiClient from "./axios";

export default {
  getMetrics() {
    return apiClient.get("/v1/evaluate/metrics");
  },
  runEvaluation(configuration_id) {
    return apiClient.post(`/v1/evaluate/${configuration_id}`);
  },
  getResultDetail(configId, runId) {
    return apiClient.get(`/v1/results/${configId}/${runId}`);
  },
};
