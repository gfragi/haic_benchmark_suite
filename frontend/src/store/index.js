import { createStore } from "vuex";
import configuration from "./modules/configuration";
import evaluation from "./modules/evaluation";
import surveys from "./modules/surveys";
import ui from "./modules/ui";

export default createStore({
  state: {
    version: "2.0.0",
  },
  getters: {
    appVersion: (state) => state.version,
  },
  mutations: {},
  actions: {},
  modules: {
    configuration,
    evaluation,
    surveys,
    ui,
  },
});
