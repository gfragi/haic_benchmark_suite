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
// Treat /survey as PUBLIC (no forced login)
const isPublicPath = () => {
  // keep it simple — if you add more public routes, extend this check
  return window.location.pathname === "/survey";
};

// keycloak
//   .init({
//     onLoad: "login-required",
//     checkLoginIframe: false,
//     redirectUri: window.location.origin,
//   })
const publicRedirect = () =>
  window.location.origin + window.location.pathname + window.location.search;

keycloak
  .init({
    onLoad: isPublicPath() ? "check-sso" : "login-required",
    checkLoginIframe: false,
    // IMPORTANT: keep query params on the public page
    redirectUri: isPublicPath()
      ? publicRedirect()
      : window.location.origin + "/",
  })
  .then(async (authenticated) => {
    console.log("Keycloak init resolved:", authenticated);
    // If not authenticated AND it’s NOT a public route, trigger login.
    if (!authenticated && !isPublicPath()) {
      console.warn("Not authenticated, redirecting to login");
      keycloak.login();
      return;
    }

    window.__kc = keycloak;

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
