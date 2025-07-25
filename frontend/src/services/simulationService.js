import axios from "axios";

const apiBase = "http://localhost:8000";

export const fetchConfigs = async () => {
  const res = await axios.get(`${apiBase}/env/list_configs`);
  return res.data.available_configs;
};

export const simulateConfig = async (name) => {
  const res = await axios.post(`${apiBase}/simulator/simulate?name=${name}`);
  return res.data.simulation_result;
};
