import apiClient from "./axios";

export const fetchSurveyAggregates = async (pilotTag = null) => {
  const params = pilotTag ? { pilot_tag: pilotTag } : {};
  const response = await apiClient.get("/v1/survey/aggregate", { params });
  return response.data;
};

export async function fetchVersions(pilotTag) {
  if (!pilotTag) return [];
  const { data } = await apiClient.get("/v1/survey/versions", {
    params: { pilot_tag: pilotTag },
  });
  // backend may return { versions: [...] } or just [...]
  return Array.isArray(data) ? data : data?.versions ?? [];
}
