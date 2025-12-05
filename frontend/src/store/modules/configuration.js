// Configuration Module - Manages evaluation configurations
export default {
  namespaced: true,

  state: {
    configurations: [],
    currentConfiguration: null,
    loading: false,
    error: null,
  },

  getters: {
    allConfigurations: (state) => state.configurations,
    currentConfig: (state) => state.currentConfiguration,
    isLoading: (state) => state.loading,
    hasError: (state) => state.error,
    configById: (state) => (id) => {
      return state.configurations.find(config => config.id === id);
    },
  },

  mutations: {
    SET_CONFIGURATIONS(state, configurations) {
      state.configurations = configurations;
    },

    ADD_CONFIGURATION(state, configuration) {
      state.configurations.push(configuration);
    },

    UPDATE_CONFIGURATION(state, { id, configuration }) {
      const index = state.configurations.findIndex(config => config.id === id);
      if (index !== -1) {
        state.configurations.splice(index, 1, { ...state.configurations[index], ...configuration });
      }
    },

    REMOVE_CONFIGURATION(state, id) {
      state.configurations = state.configurations.filter(config => config.id !== id);
    },

    SET_CURRENT_CONFIGURATION(state, configuration) {
      state.currentConfiguration = configuration;
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
    async fetchConfigurations({ commit }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch('/api/v1/configuration');
        if (!response.ok) throw new Error('Failed to fetch configurations');

        const configurations = await response.json();
        commit('SET_CONFIGURATIONS', configurations);
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching configurations:', error);
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async createConfiguration({ commit }, configData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch('/api/v1/configuration/new', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(configData),
        });

        if (!response.ok) throw new Error('Failed to create configuration');

        const configuration = await response.json();
        commit('ADD_CONFIGURATION', configuration);
        commit('SET_CURRENT_CONFIGURATION', configuration);

        return configuration;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error creating configuration:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async updateConfiguration({ commit }, { id, configData }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(`/api/v1/configuration/update/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(configData),
        });

        if (!response.ok) throw new Error('Failed to update configuration');

        const configuration = await response.json();
        commit('UPDATE_CONFIGURATION', { id, configuration });

        return configuration;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error updating configuration:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async deleteConfiguration({ commit }, id) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(`/api/v1/configuration/delete/${id}`, {
          method: 'DELETE',
        });

        if (!response.ok) throw new Error('Failed to delete configuration');

        commit('REMOVE_CONFIGURATION', id);
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error deleting configuration:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchConfigurationById({ commit }, id) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');

      try {
        const response = await fetch(`/api/v1/configuration/${id}`);
        if (!response.ok) throw new Error('Failed to fetch configuration');

        const configuration = await response.json();
        commit('SET_CURRENT_CONFIGURATION', configuration);

        return configuration;
      } catch (error) {
        commit('SET_ERROR', error.message);
        console.error('Error fetching configuration:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    clearCurrentConfiguration({ commit }) {
      commit('SET_CURRENT_CONFIGURATION', null);
    },

    clearError({ commit }) {
      commit('CLEAR_ERROR');
    },
  },
};
