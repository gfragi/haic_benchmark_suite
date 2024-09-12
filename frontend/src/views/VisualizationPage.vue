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
            @change="onGroupSelect"
          ></v-select>
        </v-col>

        <!-- X-Axis Dropdown (Evaluation Date/Model Version) -->
        <v-col cols="6">
          <v-select
            v-model="selectedXAxis"
            :items="xAxisOptions"
            label="Select X-Axis (Evaluation Date/AI Model Version)"
            @change="fetchData"
          ></v-select>
        </v-col>
      </v-row>

      <!-- Render Charts for Each Metric in the Selected Group -->
      <v-row v-if="selectedMetrics.length > 0">
        <v-col
          v-for="(metric, index) in selectedMetrics"
          :key="index"
          cols="12"
          md="6"
        >
          <!-- Render PlotChart only if chartData is available for that metric -->
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
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  components: {
    PlotChart,
    BaseLayout,
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
      selectedMetrics: [], // Metrics under the selected group
      chartData: {}, // Object to store the data for each metric
      labels: [], // Labels for the X-axis (e.g., evaluation dates or AI model versions)
    };
  },
  mounted() {
    this.configId = this.$route.params.configId; // Retrieve configId from the route
    this.fetchMetricGroups(); // Fetch the available metrics
  },
  watch: {
    $route(to, from) {
      if (to.params.configId !== from.params.configId) {
        this.configId = to.params.configId;
        this.fetchData();
      }
    },
  },
  methods: {
    // Fetch metric groups from the /evaluate/metrics endpoint
    fetchMetricGroups() {
      evaluationService
        .getMetrics()
        .then((response) => {
          this.groupedMetrics = response.data; // Assuming it's in the structure you showed
          this.groupOptions = Object.keys(this.groupedMetrics).map((group) => ({
            title: group,
            value: group,
          }));
          console.log("Fetched Grouped Metrics:", this.groupedMetrics);

          // Trigger the data fetching for the first group by default
          this.selectedGroup = this.groupOptions[0].value;
          this.onGroupSelect();
        })
        .catch((error) => {
          console.error("Error fetching metric groups:", error);
        });
    },

    // Handle the selection of a metric group and load the related metrics
    onGroupSelect() {
      if (this.selectedGroup && this.groupedMetrics[this.selectedGroup]) {
        // Set the metrics for the selected group
        this.selectedMetrics = this.groupedMetrics[this.selectedGroup];
        console.log("Selected Metrics:", this.selectedMetrics);

        // Fetch the data for the selected metrics
        this.fetchData();
      }
    },

    // Fetch results data (evaluation runs) from the backend
    fetchData() {
      if (!this.configId || !this.selectedGroup) return;

      // Fetch all available runs for the current configId
      resultService
        .getResultsByConfig(this.configId) // Modify this to fetch all runs for the config
        .then((response) => {
          const runs = response.data; // This contains all the runs for the given config

          if (!runs || runs.length === 0) {
            console.error("No run data available");
            return;
          }

          // Map the labels based on the selected X-axis field (e.g., evaluation_date)
          this.labels = runs.map((run) => run[this.selectedXAxis]); // e.g., 'evaluation_date' or 'ai_model_version'

          // Initialize chart data for each metric
          // this.selectedMetrics.forEach((metric) => {
          //   const metricKey = metric.replace(/ /g, "_").toLowerCase();
          //   this.chartData[metric] = []; // Initialize array for each metric's data
          // });

          // Loop through each run and retrieve its data
          runs.forEach((run) => {
            this.selectedMetrics.forEach((metric) => {
              const metricKey = metric.replace(/ /g, "_").toLowerCase();

              // Ensure the interaction_data object has the metric key before accessing it
              if (run.interaction_data && metricKey in run.interaction_data) {
                this.chartData[metric].push(run.interaction_data[metricKey]);
              } else {
                this.chartData[metric].push(null); // Push null if the metric data is missing
              }
            });
          });

          console.log("Chart Data:", this.chartData);
        })
        .catch((error) => {
          console.error("Error fetching run data:", error);
        });
    },
  },
};
</script>
