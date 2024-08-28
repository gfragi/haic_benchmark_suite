import apiClient from "./axios";

export default {
  getAllEvaluationResults() {
    return apiClient.get(`/evaluate/results`);
  },
  getEvaluationResultsByConfig(configuration_id) {
    return apiClient.get(`/evaluate/${configuration_id}/results`);
  },
  getEvaluationResultDetail(result_id) {
    return apiClient.get(`/evaluate/results/${result_id}`);
  },
};
