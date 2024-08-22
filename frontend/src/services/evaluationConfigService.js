import apiClient from "./axios";

export default {
  getAllConfigs() {
    return apiClient.get("/evaluation/config");
  },
  getConfigById(configId) {
    return apiClient.get(`/evaluation/config/${configId}`);
  },
  createConfig(configData) {
    return apiClient.post("/evaluation/config", configData);
  },
  updateConfig(configId, configData) {
    return apiClient.put(`/evaluation/config/${configId}`, configData);
  },
  deleteConfig(configId) {
    return apiClient.delete(`/evaluation/config/${configId}`);
  },
  getMetrics() {
    return apiClient.get("/evaluate/metrics");
  },
};
