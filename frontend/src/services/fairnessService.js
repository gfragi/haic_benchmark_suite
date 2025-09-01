import apiClient from "./axios";

export default {
  runFairnessEvaluation(feature, payload) {
    return apiClient.post(`/v1/fairness/evaluate?feature=${feature}`, payload);
  },
};
