import apiClient from "./axios";

export default {
  runFairnessEvaluation(feature, payload) {
    return apiClient.post(`/fairness/evaluate?feature=${feature}`, payload);
  },
};
