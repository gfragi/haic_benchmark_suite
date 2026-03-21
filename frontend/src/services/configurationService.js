import api from "./axios";

export default {
  getAllConfigs(skip = 0, limit = 100) {
    return api.get("/v1/configuration", { params: { skip, limit } });
  },
  getConfigById(configuration_id) {
    return api.get(`/v1/configuration/${configuration_id}`);
  },
  createConfig(configData) {
    return api.post("/v1/configuration/new", configData);
  },
  updateConfig(configuration_id, configData) {
    return api.put(`/v1/configuration/update/${configuration_id}`, configData);
  },
  deleteConfig(configuration_id) {
    return api.delete(`/v1/configuration/delete/${configuration_id}`);
  },
};

export async function generateConfig(payload) {
  // payload: { task_name, task_parameters, agent_definitions, profile_definitions }
  const { data } = await api.post("/v1/env/generate_config", payload);
  return data; // { message, path }
}

export async function listConfigs() {
  const { data } = await api.get(`/v1/env/list_configs`);
  // backend returns {available_configs:[...]}
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.available_configs)) return data.available_configs;
  return [];
}

export async function loadConfig(name) {
  const { data } = await api.get("/v1/env/load_config", {
    params: { name },
  });
  return data?.config || data;
}
