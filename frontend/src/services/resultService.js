import apiClient from "./axios";

export default {
  getResultsByConfig(configuration_id) {
    return apiClient.get(`/results/${configuration_id}`);
  },
  getResultDetail(configuration_id, result_id) {
    return apiClient.get(`/results/${configuration_id}/${result_id}`);
  },
  getResultsByConfigIdAndGroup(configuration_id, group_name) {
    return apiClient.get(`/results/${configuration_id}/${group_name}`);
  },
};
