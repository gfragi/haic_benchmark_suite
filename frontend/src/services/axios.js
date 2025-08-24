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
  baseURL: process.env.VUE_APP_API_BASE_URL,
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});
console.log("ENV:", process.env.NODE_ENV);
console.log("API base:", process.env.VUE_APP_API_BASE_URL);
export default apiClient;
