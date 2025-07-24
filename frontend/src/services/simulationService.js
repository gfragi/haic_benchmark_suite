import axios from "axios";

export const fetchConfigs = async () => {
  const res = await axios.get("/env/list_configs");
  return res.data.available_configs;
};

export const simulateConfig = async (name) => {
  const res = await axios.post(`/simulator/simulate?name=${name}`);
  return res.data.simulation_result;
};
