import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import keycloak from "./services/keycloak";

loadFonts();

keycloak
  .init({ onLoad: "login-required", checkLoginIframe: false })
  .then((authenticated) => {
    if (authenticated) {
      const app = createApp(App);
      // Optionally make keycloak available globally
      app.config.globalProperties.$keycloak = keycloak;
      app.use(router);
      app.use(store);
      app.use(vuetify);
      app.mount("#app");
    } else {
      window.location.reload();
    }
  })
  .catch(() => {
    console.error("Authentication failed");
  });
