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
        <v-col
          v-for="(metric, index) in groupedMetrics[selectedGroup]"
          :key="index"
          cols="12"
          md="6"
        >
          <!-- Ensure the component is rendered only if chartData exists -->
          <PlotChart
            v-if="chartData[metric]"
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
import evaluationService from "@/services/evaluationService"; // Assuming this service fetches the metrics

export default {
  components: {
    PlotChart,
  },
  data() {
    return {
      configId: null, // Holds the passed configId
      selectedGroup: null, // Holds the selected metric group
      selectedXAxis: "evaluation_date", // Default X-axis option
      groupOptions: [], // To be dynamically fetched
      xAxisOptions: [
        { title: "Evaluation Date", value: "evaluation_date" },
        { title: "AI Model Version", value: "ai_model_version" },
      ],
      groupedMetrics: {}, // Metrics from the /evaluate/metrics API
      chartData: {}, // Object to store the data for each metric
      labels: [], // Labels for the X-axis (e.g., evaluation dates or AI model versions)
    };
  },
  mounted() {
    this.configId = this.$route.params.configId; // Retrieve configId from the route
    this.fetchMetricGroups(); // Fetch the available metrics
    this.fetchData(); // Fetch the data when the page loads
  },
  methods: {
    // Fetch metric groups from the /evaluate/metrics endpoint
    fetchMetricGroups() {
      evaluationService
        .getMetrics()
        .then((response) => {
          this.groupedMetrics = response.data;
          this.groupOptions = Object.keys(this.groupedMetrics).map((group) => ({
            title: group,
            value: group,
          }));
          console.log("Fetched Grouped Metrics:", this.groupedMetrics);

          // Trigger the data fetching for the first group by default
          this.selectedGroup = this.groupOptions[0].value;
        })
        .catch((error) => {
          console.error("Error fetching metric groups:", error);
        });
    },

    // Fetch results data (evaluation runs) from the backend
    fetchData() {
      resultService
        .getResultsByConfig(this.configId) // Fetch results for the given configId
        .then((response) => {
          const runs = response.data;
          this.labels = runs.map((run) => run[this.selectedXAxis]); // Set the labels based on selected X-axis

          // Loop through each metric in the selected group and prepare the chart data
          Object.keys(this.groupedMetrics).forEach((group) => {
            this.groupedMetrics[group].forEach((metric) => {
              this.chartData[metric] = runs.map(
                (run) =>
                  run.interaction_data[metric.replace(/ /g, "_").toLowerCase()]
              );
            });
          });

          console.log("Prepared chartData:", this.chartData);
        })
        .catch((error) => {
          console.error("Error fetching run data:", error);
        });
    },
  },
};
</script>
