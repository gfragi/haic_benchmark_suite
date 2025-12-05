// Evaluation Module - Manages evaluation runs and results
export default {
  namespaced: true,

  state: {
    evaluations: [],
    currentEvaluation: null,
    results: [],
    currentResult: null,
    metrics: [],
    loading: false,
    error: null,
  },

  getters: {
    allEvaluations: (state) => state.evaluations,
    currentEvaluation: (state) => state.currentEvaluation,
    allResults: (state) => state.results,
    currentResult: (state) => state.currentResult,
    availableMetrics: (state) => state.metrics,
    isLoading: (state) => state.loading,
    hasError: (state) => state.error,
    evaluationById: (state) => (id) => {
      return state.evaluations.find((evaluation) => evaluation.id === id);
    },
    resultByConfigId: (state) => (configId) => {
      return state.results.filter(
        (result) => result.configuration_id === configId
      );
    },
  },

  mutations: {
    SET_EVALUATIONS(state, evaluations) {
      state.evaluations = evaluations;
    },

    ADD_EVALUATION(state, evaluation) {
      state.evaluations.push(evaluation);
    },

    UPDATE_EVALUATION(state, { id, evaluation }) {
      const index = state.evaluations.findIndex(
        (evaluation) => evaluation.id === id
      );
      if (index !== -1) {
        state.evaluations.splice(index, 1, {
          ...state.evaluations[index],
          ...evaluation,
        });
      }
    },

    SET_CURRENT_EVALUATION(state, evaluation) {
      state.currentEvaluation = evaluation;
    },

    SET_RESULTS(state, results) {
      state.results = results;
    },

    ADD_RESULT(state, result) {
      state.results.push(result);
    },

    SET_CURRENT_RESULT(state, result) {
      state.currentResult = result;
    },

    SET_METRICS(state, metrics) {
      state.metrics = metrics;
    },

    SET_LOADING(state, loading) {
      state.loading = loading;
    },

    SET_ERROR(state, error) {
      state.error = error;
    },

    CLEAR_ERROR(state) {
      state.error = null;
    },
  },

  actions: {
    async fetchEvaluations({ commit }) {
      commit("SET_LOADING", true);
      commit("CLEAR_ERROR");

      try {
        // Note: This endpoint might not exist yet, adjust as needed
        const response = await fetch("/api/v1/evaluations");
        if (!response.ok) throw new Error("Failed to fetch evaluations");

        const evaluations = await response.json();
        commit("SET_EVALUATIONS", evaluations);
      } catch (error) {
        commit("SET_ERROR", error.message);
        console.error("Error fetching evaluations:", error);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async startEvaluation({ commit }, configId) {
      commit("SET_LOADING", true);
      commit("CLEAR_ERROR");

      try {
        const response = await fetch(`/api/v1/evaluate/${configId}`, {
          method: "POST",
        });

        if (!response.ok) throw new Error("Failed to start evaluation");

        const evaluation = await response.json();
        commit("ADD_EVALUATION", evaluation);
        commit("SET_CURRENT_EVALUATION", evaluation);

        return evaluation;
      } catch (error) {
        commit("SET_ERROR", error.message);
        console.error("Error starting evaluation:", error);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchResults({ commit }, configId) {
      commit("SET_LOADING", true);
      commit("CLEAR_ERROR");

      try {
        const response = await fetch(`/api/v1/results/${configId}`);
        if (!response.ok) throw new Error("Failed to fetch results");

        const result = await response.json();
        commit("SET_CURRENT_RESULT", result);

        return result;
      } catch (error) {
        commit("SET_ERROR", error.message);
        console.error("Error fetching results:", error);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchMetrics({ commit }) {
      commit("SET_LOADING", true);
      commit("CLEAR_ERROR");

      try {
        const response = await fetch("/api/v1/evaluate/metrics");
        if (!response.ok) throw new Error("Failed to fetch metrics");

        const metrics = await response.json();
        commit("SET_METRICS", metrics);

        return metrics;
      } catch (error) {
        commit("SET_ERROR", error.message);
        console.error("Error fetching metrics:", error);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    clearCurrentEvaluation({ commit }) {
      commit("SET_CURRENT_EVALUATION", null);
    },

    clearCurrentResult({ commit }) {
      commit("SET_CURRENT_RESULT", null);
    },

    clearError({ commit }) {
      commit("CLEAR_ERROR");
    },
  },
};
