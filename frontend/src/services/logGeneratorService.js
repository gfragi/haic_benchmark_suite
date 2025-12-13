import api from "./axios";

export default {
  async generateLogs(params) {
    try {
      const response = await api.get(`/v1/log-generator/generate`, {
        params: {
          app_type: params.app_type,
          count: params.count,
          start_date: params.start_date,
          end_date: params.end_date,
          ai_model_version_range: params.ai_model_version_range,
        },
      });
      // Save the logs as a JSON file and trigger download
      this.downloadLogs(response.data);
    } catch (error) {
      console.error(
        "Error generating logs:",
        error.response?.data || error.message
      );
    }
  },
  downloadLogs(logs) {
    // Convert JSON data to a blob
    const blob = new Blob([JSON.stringify(logs, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element and trigger the download
    const a = document.createElement("a");
    a.href = url;
    a.download = "generated_logs.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Revoke the object URL after download
    URL.revokeObjectURL(url);
  },
};
