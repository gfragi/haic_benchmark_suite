import axios from "axios";

export const fetchSurveyAggregates = async (pilotTag = null) => {
  const params = pilotTag ? { pilot_tag: pilotTag } : {};
  const response = await axios.get("/survey/aggregate", { params });
  return response.data;
};
