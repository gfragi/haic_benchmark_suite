import apiClient from "./axios";

export default {
  uploadLog(logData) {
    return apiClient.post("/log", logData);
  },
};
