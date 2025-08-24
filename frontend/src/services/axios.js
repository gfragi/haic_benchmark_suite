import axios from "axios";
import keycloak from "./keycloak";

// attach token to *all* axios instances
axios.interceptors.request.use((config) => {
  const token = keycloak.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

function resolveApiBase() {
  // Vue CLI: build-time only
  let base = (process.env.VUE_APP_API_BASE_URL || "/api").trim();

  // prevent HTTPS→HTTP mixed content
  if (window.location.protocol === "https:" && base.startsWith("http://")) {
    console.error("Mixed-content API base detected:", base, "→ forcing /api");
    base = "/api";
  }
  return base;
}

const baseURL = resolveApiBase();

const apiClient = axios.create({
  baseURL,
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

console.log("ENV:", process.env.NODE_ENV);
console.log("API base (resolved):", baseURL);

export default apiClient;
