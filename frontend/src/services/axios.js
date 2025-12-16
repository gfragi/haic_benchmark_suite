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

// Interceptor to fix duplicate /v1 in endpoint URLs
api.interceptors.request.use((config) => {
  // Log request details for debugging
  console.log("API Request:", {
    baseURL: config.baseURL,
    url: config.url,
    fullURL: config.baseURL + config.url,
  });

  // Fix duplicate /v1 in endpoint paths
  // This happens when baseURL already includes /v1 and endpoint also starts with /v1
  if (config.url && config.url.startsWith("/v1/")) {
    const originalUrl = config.url;
    // Remove the leading /v1
    config.url = config.url.substring(3);
    console.warn(`Fixed duplicate /v1: ${originalUrl} → ${config.url}`);
  }

  // Also handle case where endpoint might have double slashes
  if (config.url && config.url.includes("//")) {
    config.url = config.url.replace(/\/+/g, "/");
  }

  return config;
});

// Attach bearer token if logged in (added after the URL fix)
api.interceptors.request.use((config) => {
  if (keycloak?.authenticated && keycloak?.token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${keycloak.token}`;
  }
  return config;
});

// Response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log("API Response:", {
      url: response.config.url,
      status: response.status,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.error("API Error:", {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
      fullURL: error.config?.baseURL + error.config?.url,
    });
    return Promise.reject(error);
  }
);

export default api;
