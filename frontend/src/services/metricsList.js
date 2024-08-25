import apiClient from "./axios";

export default {
  getMetrics() {
    return apiClient.get("/evaluate/metrics");
  },
};
