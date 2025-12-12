// src/services/axios.js
import axios from "axios";
import keycloak from "@/services/keycloak";

function resolveApiBase() {
  // Get base URL from environment
  let base = (
    (typeof import.meta !== "undefined" &&
      import.meta.env &&
      import.meta.env.VUE_APP_API_BASE_URL) ||
    process.env.VUE_APP_API_BASE_URL ||
    "/api"
  ).trim();

  // Ensure HTTPS when page is served over HTTPS
  if (window.location.protocol === "https:" && !base.startsWith("https://")) {
    if (base.startsWith("http://")) {
      console.error("Mixed-content API base detected:", base, "→ forcing /api");
      base = "/api";
    } else if (base.startsWith("/")) {
      // Relative URL, convert to absolute HTTPS
      base = window.location.origin + base;
    } else {
      // Some other protocol, ensure HTTPS
      base = base.replace(/^http:/, "https:");
    }
  }

  return base;
}

const api = axios.create({
  baseURL: resolveApiBase(),
  // withCredentials: true, // if need cookies
});

// Attach bearer token if logged in
api.interceptors.request.use((config) => {
  if (keycloak?.authenticated && keycloak?.token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${keycloak.token}`;
  }
  return config;
});

export default api;
