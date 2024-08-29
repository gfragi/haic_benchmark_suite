import apiClient from "./axios";

export default {
  getLogsByConfigId(configId) {
    return apiClient.get(`/logs/${configId}`);
  },
};
