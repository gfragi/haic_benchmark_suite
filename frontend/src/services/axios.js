// src/services/axios.js
import axios from "axios";
import keycloak from "@/services/keycloak";

const api = axios.create({
  baseURL:
    import.meta?.env?.VITE_API_BASE ||
    process.env.VUE_APP_API_BASE ||
    "http://localhost:8000/api",
  // withCredentials: true, // if you need cookies
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
