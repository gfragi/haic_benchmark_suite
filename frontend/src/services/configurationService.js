import apiClient from "./axios";

export default {
  getAllConfigs() {
    return apiClient.get("/v1/configuration/list/");
  },
  getConfigById(configuration_id) {
    return apiClient.get(`/v1/configuration/${configuration_id}`);
  },
  createConfig(configData) {
    return apiClient.post("/v1/configuration/new", configData);
  },
  updateConfig(configuration_id, configData) {
    return apiClient.put(
      `/v1/configuration/update/${configuration_id}`,
      configData
    );
  },
  deleteConfig(configuration_id) {
    return apiClient.delete(`/v1/configuration/delete/${configuration_id}`);
  },
};

export async function generateConfig(payload) {
  // payload: { task_name, task_parameters, agent_definitions, profile_definitions }
  const { data } = await apiClient.post("/v1/env/generate_config", payload);
  return data; // { message, path }
}

export async function listConfigs() {
  const { data } = await apiClient.get(`/v1/env/list_configs`);
  // backend returns {available_configs:[...]}
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.available_configs)) return data.available_configs;
  return [];
}

export async function loadConfig(name) {
  const { data } = await apiClient.get("/v1/env/load_config", {
    params: { name },
  });
  return data?.config || data;
}
