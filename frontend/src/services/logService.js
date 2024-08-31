import apiClient from "./axios";

export default {
  getLogsByConfigId(configId) {
    return apiClient.get(`/logs/${configId}`);
  },
  downloadLog(logName) {
    return apiClient.get(`/logs/download/${logName}`);
  },
  deleteLog(logName) {
    return apiClient.delete(`/logs/${logName}`);
  },
};
