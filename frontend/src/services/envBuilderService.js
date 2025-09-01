import api from "./axios";

export async function generateEnvConfig(payload) {
  // you already have a similar helper in configurationService; this is clearer for builder
  const { data } = await api.post("/v1/env/generate_config", payload);
  return data; // { message, path }
}

export async function runSimulation(configPath, seed = null) {
  const params = new URLSearchParams();
  if (seed !== null) params.set("seed", seed);
  const { data } = await api.post(
    "/v1/simulator/run",
    { config_path: configPath },
    { params }
  );
  return data; // { run_id, output_dir, ... }
}
