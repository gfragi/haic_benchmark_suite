import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000", // Update with your backend URL
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

export default apiClient;
