import axios from "axios";
import keycloak from "./keycloak";

axios.interceptors.request.use(
  (config) => {
    const token = keycloak.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const apiClient = axios.create({
  baseURL: "backend.benchmarking.svc.cluster.local:8000", // Update with backend URL
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

export default apiClient;
