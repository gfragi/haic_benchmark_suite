import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import keycloak from "./services/keycloak";
import { PerformancePlugin } from "./utils/performanceMonitor";

loadFonts();

console.log("Keycloak config:", {
  url: process.env.VUE_APP_KEYCLOAK_URL,
  realm: process.env.VUE_APP_KEYCLOAK_REALM,
  clientId: process.env.VUE_APP_KEYCLOAK_CLIENT_ID,
});
// Treat /survey as PUBLIC (no forced login)
const isPublicPath = () => {
  return window.location.pathname === "/survey";
};

const publicRedirect = () =>
  window.location.origin + window.location.pathname + window.location.search;

const mountApp = async (kc) => {
  window.__kc = kc;
  const app = createApp(App);
  app.config.globalProperties.$keycloak = kc;
  app.use(router);
  app.use(store);
  app.use(vuetify);
  app.use(PerformancePlugin);
  await router.isReady();
  app.mount("#app");
};

if (process.env.VUE_APP_BYPASS_AUTH === "true") {
  console.warn("Auth bypass enabled — skipping Keycloak");
  mountApp({ authenticated: true, token: "dev-token", tokenParsed: { preferred_username: "dev-user" } });
} else {
  keycloak
    .init({
      onLoad: isPublicPath() ? "check-sso" : "login-required",
      checkLoginIframe: false,
      redirectUri: isPublicPath()
        ? publicRedirect()
        : window.location.origin + "/",
    })
    .then(async (authenticated) => {
      console.log("Keycloak init resolved:", authenticated);
      if (!authenticated && !isPublicPath()) {
        console.warn("Not authenticated, redirecting to login");
        keycloak.login();
        return;
      }
      await mountApp(keycloak);
    })
    .catch((err) => {
      console.error("Keycloak init failed:", err);
    });
}
