import apiClient from "./axios";

export default {
  getMetrics() {
    return apiClient.get("/evaluation/metrics");
  },
};
