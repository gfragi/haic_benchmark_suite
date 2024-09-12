import apiClient from "./axios";

export default {
  // Fetch results for a specific configuration
  getResultsByConfig(configuration_id) {
    console.log(`Fetching results for config ID: ${configuration_id}`);
    return apiClient.get(`/results/${configuration_id}`);
  },
  // Fetch detailed result for a specific run ID
  getResultDetail(configuration_id, result_id) {
    console.log(
      `Fetching detail for config ID: ${configuration_id}, result ID: ${result_id}`
    );
    return apiClient.get(`/results/${configuration_id}/${result_id}`);
  },

  // Fetch results by group
  getResultsByConfigIdAndGroup(configuration_id, group_name) {
    console.log(
      `Fetching results for config ID: ${configuration_id}, group: ${group_name}`
    );
    return apiClient.get(`/results/${configuration_id}/group/${group_name}`);
  },
};
