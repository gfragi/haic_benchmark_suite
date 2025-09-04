import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import keycloak from "./services/keycloak";

loadFonts();

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
  .then(async (authenticated) => {
    console.log("Keycloak init resolved:", authenticated);
    if (!authenticated) {
      console.warn("Not authenticated, reloading");
      window.location.reload();
      return;
    }

    const app = createApp(App);
    app.config.globalProperties.$keycloak = keycloak;
    app.use(router);
    app.use(store);
    app.use(vuetify);

    // Wait for first route resolution (helps after SSO redirects)
    await router.isReady();

    app.mount("#app");
  })
  .catch((err) => {
    console.error("Keycloak init failed:", err);
  });
