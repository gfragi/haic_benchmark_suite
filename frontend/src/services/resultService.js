import apiClient from "./axios";

export default {
  getAllEvaluationResults() {
    return apiClient.get(`/results/list`);
  },
  getEvaluationResultsByConfig(configuration_id) {
    return apiClient.get(`/evaluate/results/${configuration_id}`);
  },
  getEvaluationResultDetail(result_id) {
    return apiClient.get(`/evaluate/results/${result_id}`);
  },
};
