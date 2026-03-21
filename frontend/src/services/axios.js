// src/services/axios.js
import axios from "axios";
import keycloak from "@/services/keycloak";

// Hardcode the production URL directly
const api = axios.create({
  baseURL: "https://benchmark.humaine-horizon.eu/api/v1",
});

console.log("🚀 Axios configured with baseURL:", api.defaults.baseURL);

// Request interceptor for auth and debugging
api.interceptors.request.use((config) => {
  // Log request for debugging
  console.log("📡 Axios Request:", {
    method: config.method?.toUpperCase(),
    url: config.baseURL + (config.url || ""),
    endpoint: config.url,
  });

  // Fix duplicate /v1 if present
  if (config.url && config.url.startsWith("/v1/")) {
    const originalUrl = config.url;
    config.url = config.url.substring(3); // Remove leading /v1
    console.log("🔄 Fixed duplicate /v1:", originalUrl, "→", config.url);
  }

  // Ensure no double slashes
  if (config.url && config.url.includes("//")) {
    config.url = config.url.replace(/\/+/g, "/");
  }

  // Add auth token
  if (keycloak?.authenticated && keycloak?.token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${keycloak.token}`;
    console.log("🔐 Added Authorization header");
  }

  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log("✅ Axios Response Success:", {
      status: response.status,
      url: response.config.url,
    });
    return response;
  },
  (error) => {
    console.error("❌ Axios Error:", {
      url: error.config?.url,
      fullUrl: error.config?.baseURL + (error.config?.url || ""),
      status: error.response?.status,
      message: error.message,
      code: error.code,
    });
    // Log the full response body — critical for FastAPI 422 errors which
    // include a 'detail' array explaining exactly which field/param is missing.
    if (error.response?.data) {
      console.error(
        "🔎 Response body:",
        JSON.stringify(error.response.data, null, 2)
      );
    }

    // Provide helpful suggestions for network errors
    if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
      console.error("🔍 Network Error - Possible causes:");
      console.error("  1. Backend server is not running");
      console.error("  2. CORS issue - check backend CORS configuration");
      console.error("  3. Mixed content - ensure all URLs use HTTPS");
      console.error("  4. Firewall or network issue");
    }

    return Promise.reject(error);
  }
);

// Export debug info
export const DEBUG_INFO = {
  pageProtocol: window.location.protocol,
  pageOrigin: window.location.origin,
  baseURL: api.defaults.baseURL,
  timestamp: new Date().toISOString(),
};

console.log("📊 Debug Info:", DEBUG_INFO);

export default api;
