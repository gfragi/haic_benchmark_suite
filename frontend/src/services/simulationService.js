// frontend/src/services/simulationService.js
import api from "./axios";

export async function simulate(configName, seed = null) {
  const params = new URLSearchParams({ name: configName });
  if (seed !== null && seed !== undefined && seed !== "") {
    params.append("seed", String(seed));
  }
  const { data } = await api.post(
    `/api/v1/simulator/simulate?${params.toString()}`
  );
  return data?.simulation_result || data; // backend returns { simulation_result: ... }
}

export async function listMetrics() {
  const { data } = await api.get("/v1/simulator/list_metrics");
  return data?.files || [];
}

export async function loadMetrics(file) {
  const { data } = await api.get("/v1/simulator/load_metrics", {
    params: { file },
  });
  return data?.metrics || data;
}
