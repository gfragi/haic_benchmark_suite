// UI Module - Manages theme, layout, and UI state
export default {
  namespaced: true,

  state: {
    theme: "light", // 'light' or 'dark'
    drawer: true, // sidebar open/closed
    loading: false, // global loading state
    notifications: [], // global notifications
    currentRoute: null,
  },

  getters: {
    isDarkTheme: (state) => state.theme === "dark",
    isDrawerOpen: (state) => state.drawer,
    isGlobalLoading: (state) => state.loading,
    allNotifications: (state) => state.notifications,
    currentRoute: (state) => state.currentRoute,
    hasNotifications: (state) => state.notifications.length > 0,
    unreadNotifications: (state) => state.notifications.filter((n) => !n.read),
  },

  mutations: {
    SET_THEME(state, theme) {
      state.theme = theme;
      localStorage.setItem("theme", theme);
    },

    TOGGLE_THEME(state) {
      state.theme = state.theme === "light" ? "dark" : "light";
      localStorage.setItem("theme", state.theme);
    },

    SET_DRAWER(state, drawer) {
      state.drawer = drawer;
    },

    TOGGLE_DRAWER(state) {
      state.drawer = !state.drawer;
    },

    SET_LOADING(state, loading) {
      state.loading = loading;
    },

    ADD_NOTIFICATION(state, notification) {
      state.notifications.unshift({
        id: Date.now(),
        read: false,
        timestamp: new Date(),
        ...notification,
      });
    },

    REMOVE_NOTIFICATION(state, id) {
      state.notifications = state.notifications.filter((n) => n.id !== id);
    },

    MARK_NOTIFICATION_READ(state, id) {
      const notification = state.notifications.find((n) => n.id === id);
      if (notification) {
        notification.read = true;
      }
    },

    CLEAR_ALL_NOTIFICATIONS(state) {
      state.notifications = [];
    },

    SET_CURRENT_ROUTE(state, route) {
      state.currentRoute = route;
    },
  },

  actions: {
    initializeTheme({ commit }) {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme && ["light", "dark"].includes(savedTheme)) {
        commit("SET_THEME", savedTheme);
      } else {
        // Check system preference
        const prefersDark =
          window.matchMedia &&
          window.matchMedia("(prefers-color-scheme: dark)").matches;
        commit("SET_THEME", prefersDark ? "dark" : "light");
      }
    },

    toggleTheme({ commit }) {
      commit("TOGGLE_THEME");
    },

    setDrawer({ commit }, drawer) {
      commit("SET_DRAWER", drawer);
    },

    toggleDrawer({ commit }) {
      commit("TOGGLE_DRAWER");
    },

    setGlobalLoading({ commit }, loading) {
      commit("SET_LOADING", loading);
    },

    showNotification({ commit }, notification) {
      commit("ADD_NOTIFICATION", notification);

      // Auto-remove after timeout if specified
      if (notification.timeout) {
        setTimeout(() => {
          commit("REMOVE_NOTIFICATION", notification.id);
        }, notification.timeout);
      }
    },

    showSuccess({ dispatch }, message) {
      dispatch("showNotification", {
        type: "success",
        message,
        timeout: 5000,
      });
    },

    showError({ dispatch }, message) {
      dispatch("showNotification", {
        type: "error",
        message,
        timeout: 10000,
      });
    },

    showWarning({ dispatch }, message) {
      dispatch("showNotification", {
        type: "warning",
        message,
        timeout: 7000,
      });
    },

    showInfo({ dispatch }, message) {
      dispatch("showNotification", {
        type: "info",
        message,
        timeout: 5000,
      });
    },

    removeNotification({ commit }, id) {
      commit("REMOVE_NOTIFICATION", id);
    },

    markNotificationRead({ commit }, id) {
      commit("MARK_NOTIFICATION_READ", id);
    },

    clearAllNotifications({ commit }) {
      commit("CLEAR_ALL_NOTIFICATIONS");
    },

    setCurrentRoute({ commit }, route) {
      commit("SET_CURRENT_ROUTE", route);
    },
  },
};
