// Surveys Module - Manages survey data and analytics
export default {
  namespaced: true,

  state: {
    surveyResponses: [],
    aggregatedData: null,
    surveyVersions: [],
    currentSurvey: null,
    loading: false,
    error: null,
  },

  getters: {
    allSurveyResponses: (state) => state.surveyResponses,
    aggregatedSurveyData: (state) => state.aggregatedData,
    availableVersions: (state) => state.surveyVersions,
    currentSurvey: (state) => state.currentSurvey,
    isLoading: (state) => state.loading,
    hasError: (state) => state.error,
    surveyByPilotTag: (state) => (pilotTag) => {
      return state.surveyResponses.filter(survey => survey.pilot_tag === pilotTag);
    },
    aggregatedByPilot: (state) => (pilotTag) => {
      if (!state.aggregatedData) return null;
      // This would need to be structured properly based on API response
      return state.aggregatedData[pilotTag] || null;
    },
  },

  mutations: {
    SET_SURVEY_RESPONSES(state, responses) {
      state.surveyResponses = responses;
    },

    ADD_SURVEY_RESPONSE(state, response) {
      state.surveyResponses.push(response);
    },

    SET_AGGREGATED_DATA(state, data) {
      state.aggregatedData = data;
    },

    SET_SURVEY_VERSIONS(state, versions) {
      state.surveyVersions = versions;
    },

    SET_CURRENT_SURVEY(state, survey) {
      state.currentSurvey = survey;
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
    async submitSurvey({ commit }, surveyData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch('/api/v1/survey', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(surveyData),
        });

        if (!response.ok) throw new Error('Failed to submit survey');

        const result = await response.json();
        commit('ADD_SURVEY_RESPONSE', surveyData);

        return result;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error submitting survey:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchAggregatedData({ commit }, pilotTag = null) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const url = pilotTag
          ? `/api/v1/survey/aggregate?pilot_tag=${encodeURIComponent(pilotTag)}`
          : '/api/v1/survey/aggregate';

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch aggregated data');

        const data = await response.json();
        commit('SET_AGGREGATED_DATA', data);

        return data;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching aggregated data:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchVersions({ commit }, pilotTag) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(`/api/v1/survey/versions?pilot_tag=${encodeURIComponent(pilotTag)}`);
        if (!response.ok) throw new Error('Failed to fetch versions');

        const versions = await response.json();
        commit('SET_SURVEY_VERSIONS', versions);

        return versions;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching versions:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchVersionSummary({ commit }, { pilotTag, appVersion }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(
          `/api/v1/survey/summary?pilot_tag=${encodeURIComponent(pilotTag)}&app_version=${encodeURIComponent(appVersion)}`
        );
        if (!response.ok) throw new Error('Failed to fetch version summary');

        const summary = await response.json();
        // Store in current survey for easy access
        commit('SET_CURRENT_SURVEY', summary);

        return summary;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching version summary:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async compareVersions({ commit }, { pilotTag, versionA, versionB }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(
          `/api/v1/survey/compare?pilot_tag=${encodeURIComponent(pilotTag)}&version_a=${encodeURIComponent(versionA)}&version_b=${encodeURIComponent(versionB)}`
        );
        if (!response.ok) throw new Error('Failed to compare versions');

        const comparison = await response.json();
        return comparison;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error comparing versions:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchQuestionAverages({ commit }, { pilotTag, appVersion }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(
          `/api/v1/survey/question-averages?pilot_tag=${encodeURIComponent(pilotTag)}&app_version=${encodeURIComponent(appVersion)}`
        );
        if (!response.ok) throw new Error('Failed to fetch question averages');

        const averages = await response.json();
        return averages;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching question averages:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    clearCurrentSurvey({ commit }) {
      commit('SET_CURRENT_SURVEY', null);
    },

    clearError({ commit }) {
      commit('CLEAR_ERROR');
    },
  },
};
