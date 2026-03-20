import api from "./axios";

export default {
  runFairnessEvaluation(feature, payload) {
    return api.post(`/v1/fairness/evaluate?feature=${feature}`, payload);
  },
};
