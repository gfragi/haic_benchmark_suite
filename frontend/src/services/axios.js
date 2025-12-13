// src/services/axios.js
import axios from "axios";
import keycloak from "@/services/keycloak";

function resolveApiBase() {
  let base =
    (typeof import.meta !== "undefined" &&
      import.meta.env &&
      import.meta.env.VUE_APP_API_BASE_URL) ||
    process.env.VUE_APP_API_BASE_URL ||
    "/api/v1";

  base = String(base).trim().replace(/\/+$/, "");
  const isHttpsPage = window.location.protocol === "https:";

  // Always use the same host as the current page
  const currentOrigin = window.location.origin;

  // If base starts with /, just prepend current origin
  if (base.startsWith("/")) {
    return currentOrigin + base;
  }

  // If base is a full URL
  if (/^https?:\/\//i.test(base)) {
    // Force HTTPS if the page is HTTPS
    if (isHttpsPage && base.startsWith("http://")) {
      console.warn("Mixed-content API base detected, upgrading to HTTPS");
      return base.replace(/^http:\/\//i, "https://");
    }
    return base;
  }

  // If it's a domain without protocol
  if (base.includes("://")) {
    const scheme = isHttpsPage ? "https://" : "http://";
    // Check if it already has a hostname
    try {
      const url = new URL(scheme + base);
      return url.toString();
    } catch {
      // If parsing fails, fall back to current origin
      return currentOrigin + "/" + base.replace(/^\/+/, "");
    }
  }

  // Default fallback
  return currentOrigin + "/" + base.replace(/^\/+/, "");
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
