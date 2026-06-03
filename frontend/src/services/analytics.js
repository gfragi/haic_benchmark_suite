import api from "./axios";

export async function getLatencyPctiles(
  configId,
  groupKey = "ai_model_version"
) {
  const { data } = await api.get(`/analytics/latency/pctiles/${configId}`, {
    params: { group_key: groupKey },
  });
  return data; // { labels, series, data, counts, sla_ms, group_key }
}
