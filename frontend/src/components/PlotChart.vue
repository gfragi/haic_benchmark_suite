<template>
  <BaseLayout>
    <v-container>
      <!-- Page Title -->
      <v-row>
        <v-col cols="12">
          <h2>Visualization for Configuration ID: {{ configId }}</h2>
        </v-col>
      </v-row>

      <!-- Metric Group Dropdown -->
      <v-row>
        <v-col cols="6">
          <v-select
            v-model="selectedGroup"
            :items="groupOptions"
            label="Select a metric group to plot"
          ></v-select>
        </v-col>

        <!-- X-Axis Dropdown (Evaluation Date/Model Version) -->
        <v-col cols="6">
          <v-select
            v-model="selectedXAxis"
            :items="xAxisOptions"
            label="Select X-Axis (Evaluation Date/AI Model Version)"
          ></v-select>
        </v-col>
      </v-row>

      <!-- Render Charts for Each Metric in the Selected Group -->
      <v-row v-if="selectedGroup">
        <!-- Ensure v-for is correctly structured -->
        <v-col
          v-for="(metric, index) in groupedMetrics[selectedGroup]"
          :key="index"
          cols="12"
          md="6"
        >
          <PlotChart
            :chartData="chartData[metric]"
            :labels="labels"
            :xAxisLabel="selectedXAxis"
            :yAxisLabel="metric"
            chartType="line"
          />
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import PlotChart from "@/components/PlotChart.vue"; // Import the reusable PlotChart component
import resultService from "@/services/resultService"; // Assuming this service fetches the results

export default {
  components: {
    PlotChart,
  },
  data() {
    return {
      configId: null, // Holds the passed configId
      selectedGroup: null, // Holds the selected metric group
      selectedXAxis: "evaluation_date", // Default X-axis option
      groupOptions: [
        { title: "Performance", value: "Performance" },
        { title: "Efficiency", value: "Efficiency" },
        {
          title: "Adaptability and Learning",
          value: "Adaptability and Learning",
        },
        {
          title: "Collaboration and Interaction",
          value: "Collaboration and Interaction",
        },
        { title: "Trust and Safety", value: "Trust and Safety" },
        {
          title: "Robustness and Generalization",
          value: "Robustness and Generalization",
        },
      ],
      xAxisOptions: [
        { title: "Evaluation Date", value: "evaluation_date" },
        { title: "AI Model Version", value: "ai_model_version" },
      ],
      groupedMetrics: {
        // These would map to the groups in your data
        Performance: [
          "Prediction Accuracy",
          "Precision",
          "Recall",
          "Overall System Accuracy",
          "Model Improvement Rate",
        ],
        Efficiency: [
          "Response Time",
          "Teaching Efficiency",
          "Query Efficiency",
          "Resource Utilization",
          "Task Completion Time",
          "Correction Efficiency",
          "Error Reduction Rate",
          "Knowledge Retention",
        ],
        // Add other metric groups here...
      },
      chartData: {}, // Object to store the data for each metric
      labels: [], // Labels for the X-axis (e.g., evaluation dates)
    };
  },
  mounted() {
    this.configId = this.$route.params.configId; // Retrieve configId from the route
    this.fetchData(); // Fetch the data when the page loads
  },
  methods: {
    fetchData() {
      resultService
        .getResultsByConfig(this.configId) // Fetch results for the given configId
        .then((response) => {
          const runs = response.data;
          this.labels = runs.map((run) => run[this.selectedXAxis]);

          // Loop through each metric and prepare the data
          Object.keys(this.groupedMetrics).forEach((group) => {
            this.groupedMetrics[group].forEach((metric) => {
              // Ensure the data is correctly populated
              if (runs.length) {
                this.chartData[metric] = runs.map(
                  (run) =>
                    run.interaction_data[
                      metric.replace(/ /g, "_").toLowerCase()
                    ]
                );
              } else {
                this.chartData[metric] = []; // Handle empty data case
              }
            });
          });
        })
        .catch((error) => {
          console.error("Error fetching run data:", error);
        });
    },
  },
};
</script>
