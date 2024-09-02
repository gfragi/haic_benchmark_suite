import apiClient from "./axios";

export default {
  getAllConfigs() {
    return apiClient.get("/configuration/list/");
  },
  getConfigById(configuration_id) {
    return apiClient.get(`/configuration/${configuration_id}`);
  },
  createConfig(configData) {
    return apiClient.post("/configuration/new", configData);
  },
  updateConfig(configuration_id, configData) {
    return apiClient.put(
      `/configuration/update/${configuration_id}`,
      configData
    );
  },
  deleteConfig(configuration_id) {
    return apiClient.delete(`/configuration/delete/${configuration_id}`);
  },
};
