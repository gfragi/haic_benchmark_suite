import api from "./axios";

export default {
  getMetrics() {
    return api.get("/v1/evaluate/metrics");
  },
  runEvaluation(configuration_id) {
    return api.post(`/v1/evaluate/${configuration_id}`);
  },
  getResultDetail(configId, runId) {
    return api.get(`/v1/results/${configId}/${runId}`);
  },
};
