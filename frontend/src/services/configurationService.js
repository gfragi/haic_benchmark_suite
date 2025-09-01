// src/services/configurationService.js
import apiClient from "./axios";

export function getAllConfigs() {
  return apiClient.get("/v1/configuration/list/");
}
export function getConfigById(configuration_id) {
  return apiClient.get(`/v1/configuration/${configuration_id}`);
}
export function createConfig(configData) {
  return apiClient.post("/v1/configuration/new", configData);
}
export function updateConfig(configuration_id, configData) {
  return apiClient.put(
    `/v1/configuration/update/${configuration_id}`,
    configData
  );
}
export function deleteConfig(configuration_id) {
  return apiClient.delete(`/v1/configuration/delete/${configuration_id}`);
}
export async function generateConfig(payload) {
  const { data } = await apiClient.post("/v1/env/generate_config", payload);
  return data;
}
export async function listConfigs() {
  const { data } = await apiClient.get("/v1/env/list_configs");
  return data?.available_configs || [];
}
export async function loadConfig(name) {
  const { data } = await apiClient.get("/v1/env/load_config", {
    params: { name },
  });
  return data?.config || data;
}
