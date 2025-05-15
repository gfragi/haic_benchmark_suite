import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import keycloak from "./services/keycloak";

loadFonts();

// Log config so you can verify it in the browser console:
console.log("Keycloak config:", {
  url: process.env.VUE_APP_KEYCLOAK_URL,
  realm: process.env.VUE_APP_KEYCLOAK_REALM,
  clientId: process.env.VUE_APP_KEYCLOAK_CLIENT_ID,
});

keycloak
  .init({
    onLoad: "login-required",
    checkLoginIframe: false,
    redirectUri: window.location.origin,
  })
  .then((authenticated) => {
    console.log("Keycloak init resolved:", authenticated);
    if (authenticated) {
      const app = createApp(App);
      app.config.globalProperties.$keycloak = keycloak;
      app.use(router);
      app.use(store);
      app.use(vuetify);
      app.mount("#app");
    } else {
      console.warn("Not authenticated, reloading");
      window.location.reload();
    }
  })
  .catch((err) => {
    console.error("Keycloak init failed:", err);
  });
