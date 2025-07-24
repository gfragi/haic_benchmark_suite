import axios from 'axios';

const API_BASE = "http://localhost:8000";

export const fetchConfigs = async () => {
  const res = await axios.get(`${API_BASE}/env/list_configs`);
  return res.data.available_configs;
};

export const simulateConfig = async (configName) => {
  const res = await axios.post(`${API_BASE}/simulator/simulate?name=${configName}`);
  return res.data.simulation_result;
};