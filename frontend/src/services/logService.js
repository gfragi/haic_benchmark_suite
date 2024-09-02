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
  uploadLog(formData, configId) {
    return apiClient.post(
      `/logs/upload?configuration_id=${configId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
  },
};
