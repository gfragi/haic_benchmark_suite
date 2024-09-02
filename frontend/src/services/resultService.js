import apiClient from "./axios";

export default {
  getAllEvaluationResults() {
    return apiClient.get(`/results/list`);
  },
  getEvaluationResultsByConfig(configuration_id) {
    return apiClient.get(`/evaluate/results/${configuration_id}`);
  },
  getEvaluationResultsDetail(result_id) {
    return apiClient.get(`/evaluate/results/${result_id}`);
  },
  getEvaluationResultDetail(configuration_id, result_id) {
    return apiClient.get(`/evaluate/results/${configuration_id}/${result_id}`);
  },
  getResultsByConfigIdAndGroup(configuration_id, group_name) {
    return apiClient.get(`/results/${configuration_id}/${group_name}`);
  },
};
