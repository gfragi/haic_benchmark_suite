import apiClient from "./axios";

export const fetchSurveyAggregates = async (pilotTag = null) => {
  const params = pilotTag ? { pilot_tag: pilotTag } : {};
  const response = await apiClient.get("/v1/survey/aggregate", { params });
  return response.data;
};
