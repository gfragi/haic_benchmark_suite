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
    "/v1/simulator/simulate",
    { config_path: configPath },
    { params }
  );
  return data; // { run_id, output_dir, ... }
}

// New functions for HAIC Sim MVP style JSON configs
export async function runHAICSimMVPConfig(configJson, seed = null) {
  // Send the HAIC config directly to the backend for processing
  const params = new URLSearchParams();
  if (seed !== null && seed !== undefined) {
    params.set("seed", String(seed));
  }

  const { data } = await api.post("/v1/simulator/simulate_haic", configJson, {
    params,
  });
  return data;
}

// Direct simulation without config file generation
export async function runDirectHAICSimulation(configJson, seed = null) {
  const params = new URLSearchParams();
  params.set("name", "direct_haic_sim");
  if (seed !== null && seed !== undefined) {
    params.set("seed", String(seed));
  }

  // For direct simulation, we need to pass the config in the request
  // This would require backend changes, so for now return a placeholder
  return {
    message:
      "Direct simulation not yet implemented. Use the config generation flow.",
    config: configJson,
  };
}

export async function runDatasetExperiment(datasetPath, mode = "baseline") {
  // This would need a backend endpoint to handle dataset experiments
  // For now, return a placeholder
  return {
    message: `Dataset experiment not yet implemented in backend. Dataset: ${datasetPath}, Mode: ${mode}`,
  };
}

// HAIC Sim MVP resource functions
export async function getHAICConfigs() {
  const { data } = await api.get("/v1/env/haic_configs");
  return data;
}

export async function loadHAICConfig(name) {
  const { data } = await api.get("/v1/env/haic_config", { params: { name } });
  return data;
}

export async function getHAICAdapters() {
  const { data } = await api.get("/v1/env/haic_adapters");
  return data;
}

export async function getHAICPlugins() {
  const { data } = await api.get("/v1/env/haic_plugins");
  return data;
}
