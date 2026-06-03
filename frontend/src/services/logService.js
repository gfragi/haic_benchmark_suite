import api from "./axios";

export default {
  getLogs(configId, page, itemsPerPage) {
    return api.get(`v1/logs/${configId}`, {
      params: { page, items_per_page: itemsPerPage },
    });
  },
  downloadLog(configId, objectKey) {
    return api.get(`v1/logs/download/${configId}`, {
      params: { object_key: objectKey },
    });
  },
  deleteLog(configId, logName) {
    return api.delete(`v1/logs/${configId}/${encodeURIComponent(logName)}`);
  },

  uploadLog(formData, configId) {
    return api.post(`/logs/upload?configuration_id=${configId}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};
