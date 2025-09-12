// src/services/axios.js
import axios from "axios";
import keycloak from "@/services/keycloak";

const api = axios.create({
  baseURL: (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VUE_APP_API_BASE_URL)
    ? import.meta.env.VUE_APP_API_BASE_URL
    : process.env.VUE_APP_API_BASE_URL,
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
