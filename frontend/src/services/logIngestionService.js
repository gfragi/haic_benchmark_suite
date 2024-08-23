import apiClient from "./axios";

export default {
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
