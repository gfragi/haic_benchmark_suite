import apiClient from "./axios";

export default {
  getLogsByConfigId(configId) {
    return apiClient.get(`/v1/logs/${configId}`);
  },
  downloadLog(logName) {
    return apiClient.get(`/v1/logs/download/${logName}`);
  },
  deleteLog(logName) {
    return apiClient.delete(`/v1/logs/${logName}`);
  },
  uploadLog(formData, configId) {
    return apiClient.post(
      `/v1/logs/upload?configuration_id=${configId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
  },
};
