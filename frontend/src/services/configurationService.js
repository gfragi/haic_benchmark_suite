// frontend/src/services/configurationService.js
import api from "./axios";

export async function generateConfig(payload) {
  // payload: { task_name, task_parameters, agent_definitions, profile_definitions }
  const { data } = await api.post("/v1/env/generate_config", payload);
  return data; // { message, path }
}

export async function listConfigs() {
  const { data } = await api.get("/v1/env/list_configs");
  return data?.available_configs || [];
}

export async function loadConfig(name) {
  const { data } = await api.get("/v1/env/load_config", {
    params: { name },
  });
  return data?.config || data;
}
